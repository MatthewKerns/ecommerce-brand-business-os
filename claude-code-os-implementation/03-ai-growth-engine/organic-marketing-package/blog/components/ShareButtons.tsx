'use client';

import { useState } from 'react';
import { Share2, Twitter, Facebook, Linkedin, Link2, Check } from 'lucide-react';

interface ShareButtonsProps {
  title: string;
  description: string;
  slug: string;
}

export function ShareButtons({ title, description, slug }: ShareButtonsProps) {
  const [copied, setCopied] = useState(false);

  const url = typeof window !== 'undefined'
    ? `${window.location.origin}/blog/${slug}`
    : '';

  const shareLinks = {
    twitter: `https://twitter.com/intent/tweet?text=${encodeURIComponent(title)}&url=${encodeURIComponent(url)}`,
    facebook: `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`,
    linkedin: `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(url)}`,
  };

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(url);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
      <div className="mb-4 flex items-center gap-2">
        <Share2 className="h-4 w-4 text-gray-600" />
        <h3 className="text-sm font-semibold text-gray-900">Share this article</h3>
      </div>

      <div className="flex flex-wrap gap-2">
        <a
          href={shareLinks.twitter}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-2 rounded-md bg-[#1DA1F2] px-4 py-2 text-sm font-medium text-white transition-opacity hover:opacity-90"
          aria-label="Share on Twitter"
        >
          <Twitter className="h-4 w-4" />
          Twitter
        </a>

        <a
          href={shareLinks.facebook}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-2 rounded-md bg-[#1877F2] px-4 py-2 text-sm font-medium text-white transition-opacity hover:opacity-90"
          aria-label="Share on Facebook"
        >
          <Facebook className="h-4 w-4" />
          Facebook
        </a>

        <a
          href={shareLinks.linkedin}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-2 rounded-md bg-[#0A66C2] px-4 py-2 text-sm font-medium text-white transition-opacity hover:opacity-90"
          aria-label="Share on LinkedIn"
        >
          <Linkedin className="h-4 w-4" />
          LinkedIn
        </a>

        <button
          onClick={copyToClipboard}
          className="flex items-center gap-2 rounded-md bg-gray-100 px-4 py-2 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-200"
          aria-label="Copy link"
        >
          {copied ? (
            <>
              <Check className="h-4 w-4" />
              Copied!
            </>
          ) : (
            <>
              <Link2 className="h-4 w-4" />
              Copy Link
            </>
          )}
        </button>
      </div>
    </div>
  );
}
