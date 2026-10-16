import { useState, useRef, useEffect } from 'react';
import { ZoomIn, ZoomOut, Maximize2, FileText, ChevronLeft, ChevronRight, Eye } from 'lucide-react';
import { ExtractedField } from '../types';

interface DocumentViewerProps {
  sessionId: string;
  docId: string;
  filename: string;
  pageCount: number;
  fields: Record<string, ExtractedField>;
  selectedField: string | null;
  onSelectField: (name: string) => void;
}

export default function DocumentViewer({
  sessionId,
  docId,
  pageCount,
  fields,
  selectedField,
  onSelectField,
}: DocumentViewerProps) {
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [zoom, setZoom] = useState<number>(1.0);
  const [imageError, setImageError] = useState<boolean>(false);
  const containerRef = useRef<HTMLDivElement>(null);

  // Reset page when docId changes
  useEffect(() => {
    setCurrentPage(1);
    setImageError(false);
  }, [docId]);

  // If selected field is on a different page, switch to that page automatically
  useEffect(() => {
    if (selectedField && fields[selectedField]?.page) {
      const targetPage = fields[selectedField].page!;
      if (targetPage !== currentPage && targetPage <= pageCount) {
        setCurrentPage(targetPage);
      }
    }
  }, [selectedField, fields, currentPage, pageCount]);

  const imageUrl = `/api/sessions/${sessionId}/documents/${docId}/pages/${currentPage}/image`;

  // Filter fields on current page that have valid bounding boxes
  const pageFields = Object.entries(fields).filter(([_, f]) => {
    return (f.page || 1) === currentPage && f.bbox && f.bbox.length === 4;
  });

  return (
    <div className="bg-[#0b1120]/90 backdrop-blur-md border border-slate-800/80 rounded-2xl overflow-hidden shadow-2xl flex flex-col h-full min-h-[580px]">
      {/* Top Action Bar */}
      <div className="px-4 py-3 bg-[#0d1629]/90 border-b border-slate-800/80 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <div className="p-1.5 bg-sky-500/10 border border-sky-500/20 rounded-lg text-sky-400">
            <Eye className="w-4 h-4" />
          </div>
          <div>
            <h4 className="text-xs font-semibold text-white tracking-tight flex items-center space-x-1.5">
              <span>Interactive Document Canvas</span>
              <span className="text-[10px] font-mono px-1.5 py-0.2 bg-slate-800 border border-slate-700/60 rounded text-slate-400">
                Live Render
              </span>
            </h4>
            <p className="text-[11px] text-slate-400">
              Interactive bounding boxes mapped from independent OCR tokens
            </p>
          </div>
        </div>

        {/* Zoom & Page Controls */}
        <div className="flex items-center space-x-2 text-xs">
          {pageCount > 1 && (
            <div className="flex items-center space-x-1 bg-slate-900 border border-slate-800 rounded-lg px-2 py-1 text-slate-300">
              <button
                onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                disabled={currentPage <= 1}
                className="p-0.5 hover:text-white disabled:opacity-30"
              >
                <ChevronLeft className="w-3.5 h-3.5" />
              </button>
              <span className="font-mono text-[11px] px-1">
                {currentPage} / {pageCount}
              </span>
              <button
                onClick={() => setCurrentPage((p) => Math.min(pageCount, p + 1))}
                disabled={currentPage >= pageCount}
                className="p-0.5 hover:text-white disabled:opacity-30"
              >
                <ChevronRight className="w-3.5 h-3.5" />
              </button>
            </div>
          )}

          <div className="flex items-center space-x-1 bg-slate-900 border border-slate-800 rounded-lg p-1">
            <button
              onClick={() => setZoom((z) => Math.max(0.6, z - 0.15))}
              className="p-1 text-slate-400 hover:text-white rounded hover:bg-slate-800"
              title="Zoom Out"
            >
              <ZoomOut className="w-3.5 h-3.5" />
            </button>
            <span className="font-mono text-[10px] text-slate-400 px-1">
              {Math.round(zoom * 100)}%
            </span>
            <button
              onClick={() => setZoom((z) => Math.min(1.8, z + 0.15))}
              className="p-1 text-slate-400 hover:text-white rounded hover:bg-slate-800"
              title="Zoom In"
            >
              <ZoomIn className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => setZoom(1.0)}
              className="p-1 text-slate-400 hover:text-sky-400 rounded hover:bg-slate-800"
              title="Reset Zoom"
            >
              <Maximize2 className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

      {/* Main Document Viewport */}
      <div
        ref={containerRef}
        className="flex-1 overflow-auto p-4 flex items-center justify-center bg-[#070b14]/70 relative select-none"
      >
        <div
          className="relative transition-transform duration-150 origin-top shadow-2xl rounded-sm bg-white overflow-hidden max-w-full"
          style={{ transform: `scale(${zoom})` }}
        >
          {imageError ? (
            <div className="w-[520px] h-[680px] bg-slate-900 border border-slate-800 flex flex-col items-center justify-center text-slate-500 p-8 text-center">
              <FileText className="w-12 h-12 text-slate-700 mb-3" />
              <p className="text-sm font-semibold text-slate-300">Document Bitmap Rasterizing</p>
              <p className="text-xs text-slate-500 mt-1">
                Visual preview loading from session storage...
              </p>
            </div>
          ) : (
            <div className="relative inline-block">
              <img
                src={imageUrl}
                alt={`Page ${currentPage}`}
                onError={() => setImageError(true)}
                className="block max-w-[580px] md:max-w-[660px] h-auto object-contain select-none pointer-events-none"
              />

              {/* Bounding Box SVG Overlay */}
              <svg className="absolute inset-0 w-full h-full pointer-events-auto">
                {pageFields.map(([name, f]) => {
                  const [x0, y0, x1, y1] = f.bbox!;
                  const isSelected = selectedField === name;
                  const isSupported = f.status === 'Supported';
                  const isInconsistent = f.status === 'Inconsistent';

                  const strokeColor = isSelected
                    ? '#0ea5e9' // Electric Cyan / Brand Sky
                    : isSupported
                    ? 'rgba(16, 185, 129, 0.45)' // Emerald
                    : isInconsistent
                    ? 'rgba(244, 63, 94, 0.65)' // Rose
                    : 'rgba(245, 158, 11, 0.45)'; // Amber

                  const fillColor = isSelected
                    ? 'rgba(14, 165, 233, 0.22)'
                    : isSupported
                    ? 'rgba(16, 185, 129, 0.08)'
                    : isInconsistent
                    ? 'rgba(244, 63, 94, 0.12)'
                    : 'rgba(245, 158, 11, 0.08)';

                  return (
                    <g key={name} className="cursor-pointer group" onClick={() => onSelectField(name)}>
                      <rect
                        x={`${x0 * 100}%`}
                        y={`${y0 * 100}%`}
                        width={`${Math.max(2, (x1 - x0) * 100)}%`}
                        height={`${Math.max(1.8, (y1 - y0) * 100)}%`}
                        fill={fillColor}
                        stroke={strokeColor}
                        strokeWidth={isSelected ? '2.5' : '1.2'}
                        strokeDasharray={isSelected ? undefined : '3, 2'}
                        rx="3"
                        className={`transition-all duration-150 ${isSelected ? 'animate-pulse' : 'hover:opacity-100'}`}
                      />
                      {isSelected && (
                        <foreignObject
                          x={`${x0 * 100}%`}
                          y={`${Math.max(0, y0 * 100 - 4)}%`}
                          width="240"
                          height="28"
                          className="overflow-visible pointer-events-none"
                        >
                          <div className="inline-flex items-center space-x-1 px-1.5 py-0.5 bg-sky-500 text-slate-950 font-bold font-mono text-[9px] rounded shadow-md whitespace-nowrap">
                            <span>{name}</span>
                            <span className="text-[8px] bg-slate-950 text-sky-300 px-1 rounded-xs font-normal">
                              {f.normalized_value ?? f.value}
                            </span>
                          </div>
                        </foreignObject>
                      )}
                    </g>
                  );
                })}
              </svg>
            </div>
          )}
        </div>
      </div>

      {/* Bottom Hint Ribbon */}
      <div className="px-4 py-2 bg-[#090e1a] border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-400">
        <div className="flex items-center space-x-3">
          <span className="flex items-center space-x-1">
            <span className="w-2.5 h-2.5 rounded-xs bg-emerald-500/30 border border-emerald-500/70 inline-block" />
            <span>Supported</span>
          </span>
          <span className="flex items-center space-x-1">
            <span className="w-2.5 h-2.5 rounded-xs bg-rose-500/30 border border-rose-500/70 inline-block" />
            <span>Inconsistent</span>
          </span>
          <span className="flex items-center space-x-1">
            <span className="w-2.5 h-2.5 rounded-xs bg-amber-500/30 border border-amber-500/70 inline-block" />
            <span>Uncertain</span>
          </span>
          <span className="flex items-center space-x-1">
            <span className="w-2.5 h-2.5 rounded-xs bg-sky-500/50 border-2 border-sky-400 inline-block animate-pulse" />
            <span className="text-sky-300 font-medium">Selected Field</span>
          </span>
        </div>
        <span className="font-mono text-[10px] text-slate-500">
          Click any bounding box or table row to inspect
        </span>
      </div>
    </div>
  );
}
