import { useState, useRef, useEffect } from 'react';
import { ZoomIn, ZoomOut, Maximize2, FileText, ChevronLeft, ChevronRight, Layers, Eye } from 'lucide-react';
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
  filename,
  pageCount,
  fields,
  selectedField,
  onSelectField,
}: DocumentViewerProps) {
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [zoom, setZoom] = useState<number>(1.0);
  const [showOverlays, setShowOverlays] = useState<boolean>(true);
  const [imageError, setImageError] = useState<boolean>(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setCurrentPage(1);
    setImageError(false);
  }, [docId]);

  useEffect(() => {
    if (selectedField && fields[selectedField]?.page) {
      const targetPage = fields[selectedField].page!;
      if (targetPage !== currentPage && targetPage <= pageCount) {
        setCurrentPage(targetPage);
      }
    }
  }, [selectedField, fields, currentPage, pageCount]);

  const imageUrl = `/api/sessions/${sessionId}/documents/${docId}/pages/${currentPage}/image`;

  const pageFields = Object.entries(fields).filter(([_, f]) => {
    return (f.page || 1) === currentPage && f.bbox && f.bbox.length === 4;
  });

  return (
    <div className="bg-[#111827] border border-slate-800 rounded-xl overflow-hidden shadow-sm flex flex-col h-full min-h-[620px]">
      {/* Viewer Header / Toolbar */}
      <div className="px-4 py-2.5 bg-[#161F30] border-b border-slate-800 flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center space-x-2.5">
          <div className="w-7 h-7 rounded-md bg-slate-800 flex items-center justify-center text-slate-300">
            <Eye className="w-4 h-4 text-blue-400" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-xs font-semibold text-white tracking-tight">{filename}</span>
              <span className="text-[10px] font-mono text-slate-400 bg-slate-800/90 px-1.5 py-0.5 rounded border border-slate-700/60">
                200 DPI Render
              </span>
            </div>
            <p className="text-[11px] text-slate-400">
              Visual grounding overlay mapped from OCR token bounding boxes
            </p>
          </div>
        </div>

        {/* Action Controls */}
        <div className="flex items-center space-x-2 text-xs">
          {/* Toggle Bounding Boxes */}
          <button
            onClick={() => setShowOverlays(!showOverlays)}
            className={`px-2 py-1 rounded-md text-[11px] font-medium border flex items-center space-x-1.5 transition-colors ${
              showOverlays
                ? 'bg-blue-600/15 border-blue-500/40 text-blue-300'
                : 'bg-slate-800 border-slate-700 text-slate-400 hover:text-slate-200'
            }`}
            title="Toggle Bounding Boxes"
          >
            <Layers className="w-3.5 h-3.5" />
            <span>Overlays</span>
          </button>

          {/* Page Selector */}
          {pageCount > 1 && (
            <div className="flex items-center space-x-1 bg-[#111827] border border-slate-800 rounded-md px-1.5 py-0.5 text-slate-300">
              <button
                onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                disabled={currentPage <= 1}
                className="p-1 hover:text-white disabled:opacity-30"
              >
                <ChevronLeft className="w-3.5 h-3.5" />
              </button>
              <span className="font-mono text-[11px] px-1 text-slate-300">
                {currentPage} / {pageCount}
              </span>
              <button
                onClick={() => setCurrentPage((p) => Math.min(pageCount, p + 1))}
                disabled={currentPage >= pageCount}
                className="p-1 hover:text-white disabled:opacity-30"
              >
                <ChevronRight className="w-3.5 h-3.5" />
              </button>
            </div>
          )}

          {/* Zoom Controls */}
          <div className="flex items-center space-x-1 bg-[#111827] border border-slate-800 rounded-md p-0.5">
            <button
              onClick={() => setZoom((z) => Math.max(0.6, z - 0.15))}
              className="p-1 text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded"
              title="Zoom Out"
            >
              <ZoomOut className="w-3.5 h-3.5" />
            </button>
            <span className="font-mono text-[11px] text-slate-400 px-1.5 min-w-[36px] text-center">
              {Math.round(zoom * 100)}%
            </span>
            <button
              onClick={() => setZoom((z) => Math.min(1.8, z + 0.15))}
              className="p-1 text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded"
              title="Zoom In"
            >
              <ZoomIn className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => setZoom(1.0)}
              className="p-1 text-slate-400 hover:text-blue-400 hover:bg-slate-800 rounded"
              title="Fit to 100%"
            >
              <Maximize2 className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

      {/* Main Document Canvas Viewport */}
      <div
        ref={containerRef}
        className="flex-1 overflow-auto p-6 flex items-start justify-center bg-[#0B0F17] relative select-none"
      >
        <div
          className="relative transition-transform duration-100 origin-top shadow-xl border border-slate-700/60 bg-white rounded-xs overflow-hidden max-w-full"
          style={{ transform: `scale(${zoom})` }}
        >
          {imageError ? (
            <div className="w-[520px] h-[680px] bg-[#111827] border border-slate-800 flex flex-col items-center justify-center text-slate-400 p-8 text-center">
              <FileText className="w-10 h-10 text-slate-600 mb-2" />
              <p className="text-xs font-semibold text-slate-300">Rendering Document Preview</p>
              <p className="text-[11px] text-slate-500 mt-1 max-w-xs">
                Extracting high-resolution page canvas from session cache...
              </p>
            </div>
          ) : (
            <div className="relative inline-block">
              <img
                src={imageUrl}
                alt={`Page ${currentPage}`}
                onError={() => setImageError(true)}
                className="block max-w-[560px] md:max-w-[640px] h-auto object-contain select-none pointer-events-none"
              />

              {/* Bounding Box SVG Layer */}
              {showOverlays && (
                <svg className="absolute inset-0 w-full h-full pointer-events-auto">
                  {pageFields.map(([name, f]) => {
                    const [x0, y0, x1, y1] = f.bbox!;
                    const isSelected = selectedField === name;
                    const isSupported = f.status === 'Supported';
                    const isInconsistent = f.status === 'Inconsistent';

                    // Non-neon, human-designed palette
                    const strokeColor = isSelected
                      ? '#2563EB' // Solid enterprise blue
                      : isSupported
                      ? '#059669' // Forest Emerald
                      : isInconsistent
                      ? '#DC2626' // Clear Red
                      : '#D97706'; // Muted Amber

                    const fillColor = isSelected
                      ? 'rgba(37, 99, 235, 0.16)'
                      : isSupported
                      ? 'rgba(5, 150, 105, 0.08)'
                      : isInconsistent
                      ? 'rgba(220, 38, 38, 0.12)'
                      : 'rgba(217, 119, 6, 0.08)';

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
                          strokeDasharray={isSelected ? undefined : '2, 2'}
                          rx="2"
                        />
                        {isSelected && (
                          <foreignObject
                            x={`${x0 * 100}%`}
                            y={`${Math.max(0, y0 * 100 - 3.8)}%`}
                            width="260"
                            height="24"
                            className="overflow-visible pointer-events-none"
                          >
                            <div className="inline-flex items-center space-x-1.5 px-2 py-0.5 bg-blue-600 text-white font-mono text-[9px] font-semibold rounded shadow-sm whitespace-nowrap">
                              <span>{name}</span>
                              <span className="text-[8px] opacity-80 border-l border-blue-400 pl-1 font-normal">
                                {f.normalized_value ?? f.value}
                              </span>
                            </div>
                          </foreignObject>
                        )}
                      </g>
                    );
                  })}
                </svg>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Viewer Footer Legend */}
      <div className="px-4 py-2 bg-[#161F30] border-t border-slate-800 flex items-center justify-between text-[11px] text-slate-400">
        <div className="flex items-center space-x-3">
          <span className="flex items-center space-x-1.5">
            <span className="w-2 h-2 rounded-xs bg-emerald-600 inline-block" />
            <span className="text-slate-300">Supported</span>
          </span>
          <span className="flex items-center space-x-1.5">
            <span className="w-2 h-2 rounded-xs bg-rose-600 inline-block" />
            <span className="text-slate-300">Inconsistent</span>
          </span>
          <span className="flex items-center space-x-1.5">
            <span className="w-2 h-2 rounded-xs bg-amber-600 inline-block" />
            <span className="text-slate-300">Uncertain</span>
          </span>
          <span className="flex items-center space-x-1.5">
            <span className="w-2 h-2 rounded-xs bg-blue-600 inline-block" />
            <span className="text-blue-400 font-medium">Selected Field</span>
          </span>
        </div>
        <span className="font-mono text-[10px] text-slate-500">
          Click any bounding box or table row to inspect
        </span>
      </div>
    </div>
  );
}
