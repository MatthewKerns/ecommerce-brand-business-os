/**
 * Personalization Rules Engine - Evaluate and apply personalization rules
 *
 * Features:
 * - Rule evaluation based on Lead data
 * - Multiple condition operators
 * - AND/OR logic for combining conditions
 * - Content transformation based on rules
 * - Support for source, interest, and custom field matching
 */

import type { Lead, LeadCustomField } from '@/types/lead';

// ============================================================
// Types
// ============================================================

export type PersonalizationOperator =
  | 'equals'
  | 'not_equals'
  | 'contains'
  | 'not_contains'
  | 'greater_than'
  | 'less_than'
  | 'greater_than_or_equal'
  | 'less_than_or_equal'
  | 'exists'
  | 'not_exists'
  | 'in'
  | 'not_in';

export type PersonalizationLogic = 'and' | 'or';

export interface PersonalizationCondition {
  field: string;
  operator: PersonalizationOperator;
  value?: any;
  logic?: PersonalizationLogic;
}

export interface PersonalizationRule {
  id: string;
  name: string;
  description?: string;
  conditions: PersonalizationCondition[];
  transformations: PersonalizationTransformation[];
  priority?: number; // Higher priority rules evaluated first
  active?: boolean;
}

export interface PersonalizationTransformation {
  type: 'replace' | 'append' | 'prepend' | 'set_variable' | 'modify_tone' | 'modify_length';
  target: string; // Field to transform (e.g., 'subject', 'body', 'variables.greeting')
  value: any;
  condition?: string; // Optional secondary condition
}

export interface PersonalizationContext {
  lead: Lead;
  variables?: Record<string, any>;
  metadata?: Record<string, any>;
}

export interface PersonalizationResult {
  matched: boolean;
  rulesApplied: string[]; // IDs of rules that were applied
  transformedVariables: Record<string, any>;
  metadata?: Record<string, any>;
}

// ============================================================
// Personalization Rules Engine Class
// ============================================================

export class PersonalizationRulesEngine {
  private rules: Map<string, PersonalizationRule> = new Map();

  constructor(rules?: PersonalizationRule[]) {
    rules?.forEach(rule => this.addRule(rule));
  }

  /**
   * Add a personalization rule
   */
  addRule(rule: PersonalizationRule): void {
    this.rules.set(rule.id, rule);
  }

  /**
   * Remove a personalization rule
   */
  removeRule(ruleId: string): boolean {
    return this.rules.delete(ruleId);
  }

  /**
   * Get rule by ID
   */
  getRule(ruleId: string): PersonalizationRule | undefined {
    return this.rules.get(ruleId);
  }

  /**
   * List all rules
   */
  listRules(filter?: { active?: boolean }): PersonalizationRule[] {
    let rules = Array.from(this.rules.values());

    if (filter?.active !== undefined) {
      rules = rules.filter(r => r.active === filter.active);
    }

    // Sort by priority (highest first)
    return rules.sort((a, b) => (b.priority || 0) - (a.priority || 0));
  }

  /**
   * Evaluate all rules against a lead and apply transformations
   */
  evaluateRules(context: PersonalizationContext): PersonalizationResult {
    const { lead, variables = {} } = context;
    const rulesApplied: string[] = [];
    let transformedVariables = { ...variables };

    // Get active rules sorted by priority
    const activeRules = this.listRules({ active: true });

    // Evaluate each rule
    for (const rule of activeRules) {
      if (this.evaluateConditions(lead, rule.conditions)) {
        // Apply transformations
        transformedVariables = this.applyTransformations(
          transformedVariables,
          rule.transformations,
          context
        );
        rulesApplied.push(rule.id);
      }
    }

    return {
      matched: rulesApplied.length > 0,
      rulesApplied,
      transformedVariables,
      metadata: {
        totalRulesEvaluated: activeRules.length,
        rulesMatched: rulesApplied.length,
      },
    };
  }

  /**
   * Evaluate a single rule against a lead
   */
  evaluateRule(lead: Lead, ruleId: string): boolean {
    const rule = this.rules.get(ruleId);
    if (!rule || rule.active === false) {
      return false;
    }

    return this.evaluateConditions(lead, rule.conditions);
  }

  /**
   * Evaluate conditions with AND/OR logic
   */
  evaluateConditions(lead: Lead, conditions: PersonalizationCondition[]): boolean {
    if (conditions.length === 0) {
      return true;
    }

    let result = true;
    let logic: PersonalizationLogic = 'and';

    for (const condition of conditions) {
      const conditionMet = this.evaluateCondition(lead, condition);

      if (logic === 'and') {
        result = result && conditionMet;
      } else {
        result = result || conditionMet;
      }

      // Update logic for next iteration
      logic = condition.logic || 'and';
    }

    return result;
  }

  /**
   * Evaluate a single condition
   */
  private evaluateCondition(lead: Lead, condition: PersonalizationCondition): boolean {
    const fieldValue = this.getFieldValue(lead, condition.field);

    switch (condition.operator) {
      case 'equals':
        return fieldValue === condition.value;

      case 'not_equals':
        return fieldValue !== condition.value;

      case 'contains':
        if (typeof fieldValue === 'string') {
          return fieldValue.includes(String(condition.value));
        }
        if (Array.isArray(fieldValue)) {
          return fieldValue.includes(condition.value);
        }
        return false;

      case 'not_contains':
        if (typeof fieldValue === 'string') {
          return !fieldValue.includes(String(condition.value));
        }
        if (Array.isArray(fieldValue)) {
          return !fieldValue.includes(condition.value);
        }
        return true;

      case 'greater_than':
        return Number(fieldValue) > Number(condition.value);

      case 'less_than':
        return Number(fieldValue) < Number(condition.value);

      case 'greater_than_or_equal':
        return Number(fieldValue) >= Number(condition.value);

      case 'less_than_or_equal':
        return Number(fieldValue) <= Number(condition.value);

      case 'exists':
        return fieldValue !== null && fieldValue !== undefined;

      case 'not_exists':
        return fieldValue === null || fieldValue === undefined;

      case 'in':
        if (!Array.isArray(condition.value)) {
          return false;
        }
        return condition.value.includes(fieldValue);

      case 'not_in':
        if (!Array.isArray(condition.value)) {
          return true;
        }
        return !condition.value.includes(fieldValue);

      default:
        return false;
    }
  }

  /**
   * Get field value from lead, supporting nested paths and custom fields
   */
  private getFieldValue(lead: Lead, field: string): any {
    // Handle custom fields specially
    if (field.startsWith('customFields.')) {
      const customFieldKey = field.substring('customFields.'.length);
      const customField = lead.customFields.find(cf => cf.key === customFieldKey);
      return customField?.value;
    }

    // Handle nested fields
    const parts = field.split('.');
    let value: any = lead;

    for (const part of parts) {
      if (value === null || value === undefined) {
        return null;
      }
      value = value[part];
    }

    return value;
  }

  /**
   * Apply transformations to variables
   */
  private applyTransformations(
    variables: Record<string, any>,
    transformations: PersonalizationTransformation[],
    context: PersonalizationContext
  ): Record<string, any> {
    const result = { ...variables };

    for (const transformation of transformations) {
      const { type, target, value } = transformation;

      switch (type) {
        case 'set_variable': {
          // Handle nested paths
          const parts = target.split('.');
          if (parts.length === 1) {
            result[target] = value;
          } else {
            // Set nested value
            let current = result;
            for (let i = 0; i < parts.length - 1; i++) {
              if (!current[parts[i]]) {
                current[parts[i]] = {};
              }
              current = current[parts[i]];
            }
            current[parts[parts.length - 1]] = value;
          }
          break;
        }

        case 'replace': {
          if (result[target] && typeof result[target] === 'string') {
            // If value is a pattern object with 'from' and 'to'
            if (typeof value === 'object' && value.from && value.to) {
              result[target] = result[target].replace(
                new RegExp(value.from, 'g'),
                value.to
              );
            } else {
              result[target] = value;
            }
          }
          break;
        }

        case 'append': {
          if (result[target]) {
            result[target] = String(result[target]) + String(value);
          } else {
            result[target] = value;
          }
          break;
        }

        case 'prepend': {
          if (result[target]) {
            result[target] = String(value) + String(result[target]);
          } else {
            result[target] = value;
          }
          break;
        }

        case 'modify_tone': {
          // Store tone preference in variables
          result['_tone'] = value;
          break;
        }

        case 'modify_length': {
          // Store length preference in variables
          result['_length'] = value;
          break;
        }
      }
    }

    return result;
  }

  /**
   * Get personalization suggestions for a lead
   */
  getPersonalizationSuggestions(lead: Lead): {
    ruleId: string;
    ruleName: string;
    description?: string;
  }[] {
    const suggestions: {
      ruleId: string;
      ruleName: string;
      description?: string;
    }[] = [];

    const activeRules = this.listRules({ active: true });

    for (const rule of activeRules) {
      if (this.evaluateConditions(lead, rule.conditions)) {
        suggestions.push({
          ruleId: rule.id,
          ruleName: rule.name,
          description: rule.description,
        });
      }
    }

    return suggestions;
  }

  /**
   * Test a rule against sample data
   */
  testRule(ruleId: string, lead: Lead): {
    matched: boolean;
    conditionsResults: Array<{
      field: string;
      operator: string;
      value: any;
      actualValue: any;
      passed: boolean;
    }>;
  } {
    const rule = this.rules.get(ruleId);
    if (!rule) {
      throw new Error(`Rule not found: ${ruleId}`);
    }

    const conditionsResults = rule.conditions.map(condition => {
      const actualValue = this.getFieldValue(lead, condition.field);
      const passed = this.evaluateCondition(lead, condition);

      return {
        field: condition.field,
        operator: condition.operator,
        value: condition.value,
        actualValue,
        passed,
      };
    });

    const matched = this.evaluateConditions(lead, rule.conditions);

    return {
      matched,
      conditionsResults,
    };
  }
}

// ============================================================
// Helper Functions
// ============================================================

/**
 * Create a source-based personalization rule
 */
export function createSourceRule(
  source: string,
  transformations: PersonalizationTransformation[]
): PersonalizationRule {
  return {
    id: `source_${source}`,
    name: `Source: ${source}`,
    description: `Personalization for leads from ${source}`,
    conditions: [
      {
        field: 'source',
        operator: 'equals',
        value: source,
      },
    ],
    transformations,
    priority: 50,
    active: true,
  };
}

/**
 * Create an interest-based personalization rule
 */
export function createInterestRule(
  interestTag: string,
  transformations: PersonalizationTransformation[]
): PersonalizationRule {
  return {
    id: `interest_${interestTag}`,
    name: `Interest: ${interestTag}`,
    description: `Personalization for leads interested in ${interestTag}`,
    conditions: [
      {
        field: 'tags',
        operator: 'contains',
        value: interestTag,
      },
    ],
    transformations,
    priority: 40,
    active: true,
  };
}

/**
 * Create a custom field-based personalization rule
 */
export function createCustomFieldRule(
  fieldKey: string,
  operator: PersonalizationOperator,
  value: any,
  transformations: PersonalizationTransformation[]
): PersonalizationRule {
  return {
    id: `custom_${fieldKey}_${operator}`,
    name: `Custom Field: ${fieldKey}`,
    description: `Personalization based on custom field ${fieldKey}`,
    conditions: [
      {
        field: `customFields.${fieldKey}`,
        operator,
        value,
      },
    ],
    transformations,
    priority: 30,
    active: true,
  };
}

/**
 * Create a segment-based personalization rule
 */
export function createSegmentRule(
  segment: string,
  transformations: PersonalizationTransformation[]
): PersonalizationRule {
  return {
    id: `segment_${segment}`,
    name: `Segment: ${segment}`,
    description: `Personalization for leads in ${segment} segment`,
    conditions: [
      {
        field: 'segments',
        operator: 'contains',
        value: segment,
      },
    ],
    transformations,
    priority: 60,
    active: true,
  };
}
