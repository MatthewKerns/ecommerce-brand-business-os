import { Loader2 } from "lucide-react";

export default function TikTokLoading() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh]">
      <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      <p className="mt-4 text-sm text-slate-600">Loading TikTok Content Studio...</p>
      <p className="mt-2 text-xs text-slate-500">Preparing your content creation tools</p>
    </div>
  );
}