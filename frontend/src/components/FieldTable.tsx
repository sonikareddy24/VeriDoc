import { CheckCircle2, XCircle, HelpCircle, Eye, AlertCircle } from 'lucide-react';
import { ExtractedField, FieldStatus } from '../types';

interface FieldTableProps {
  fields: Record<string, ExtractedField>;
  selectedField: string | null;
  onSelectField: (fieldName: string) => void;
}

export default function FieldTable({ fields, selectedField, onSelectField }: FieldTableProps) {
  const getStatusBadge = (status: FieldStatus) => {
    switch (status) {
      case 'Supported':
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
            <CheckCircle2 className="w-3 h-3" />
            <span>Supported</span>
          </span>
        );
      case 'Inconsistent':
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-rose-500/10 text-rose-400 border border-rose-500/30">
            <XCircle className="w-3 h-3" />
            <span>Inconsistent</span>
          </span>
        );
      case 'Uncertain':
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-amber-500/10 text-amber-400 border border-amber-500/30">
            <HelpCircle className="w-3 h-3" />
            <span>Uncertain</span>
          </span>
        );
      case 'Unreadable':
      default:
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-slate-800 text-slate-400 border border-slate-700">
            <AlertCircle className="w-3 h-3" />
            <span>Unreadable</span>
          </span>
        );
    }
  };

  const fieldEntries = Object.entries(fields);

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-xl">
      <div className="p-4 border-b border-slate-800 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-white">Extracted Semantic Fields</h3>
          <p className="text-xs text-slate-400">Click any row to inspect independent evidence & token grounding</p>
        </div>
        <span className="text-xs font-mono text-slate-400 bg-slate-800 px-2 py-0.5 rounded border border-slate-700">
          {fieldEntries.length} Fields Tracked
        </span>
      </div>

      <div className="overflow-x-auto max-h-[480px] overflow-y-auto">
        <table className="w-full text-left text-xs">
          <thead className="bg-slate-950/60 text-slate-400 font-semibold border-b border-slate-800 sticky top-0 backdrop-blur-sm z-10">
            <tr>
              <th className="py-2.5 px-4">Field Name</th>
              <th className="py-2.5 px-4">Extracted Value</th>
              <th className="py-2.5 px-4">Normalized</th>
              <th className="py-2.5 px-4">Verification Status</th>
              <th className="py-2.5 px-4">Engine / OCR Conf</th>
              <th className="py-2.5 px-4 text-right">Inspect</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 font-mono text-slate-300">
            {fieldEntries.map(([name, field]) => {
              const isSelected = selectedField === name;
              const displayVal = field.value !== null && field.value !== undefined ? String(field.value) : '—';
              const normVal = field.normalized_value !== null && field.normalized_value !== undefined ? String(field.normalized_value) : '—';

              return (
                <tr
                  key={name}
                  onClick={() => onSelectField(name)}
                  className={`cursor-pointer transition-colors ${
                    isSelected ? 'bg-sky-500/10 text-white' : 'hover:bg-slate-800/40'
                  }`}
                >
                  <td className="py-2.5 px-4 font-sans font-medium text-slate-200 capitalize">
                    {name.replace(/_/g, ' ')}
                  </td>
                  <td className="py-2.5 px-4 truncate max-w-[140px]" title={displayVal}>
                    {displayVal}
                  </td>
                  <td className="py-2.5 px-4 text-sky-400 font-bold truncate max-w-[140px]" title={normVal}>
                    {normVal}
                  </td>
                  <td className="py-2.5 px-4 font-sans">
                    {getStatusBadge(field.status)}
                  </td>
                  <td className="py-2.5 px-4 text-[11px] text-slate-400 font-sans">
                    <div>{field.extractor}</div>
                    {field.ocr_confidence !== undefined && field.ocr_confidence !== null && (
                      <div className="text-[10px] text-slate-500">
                        OCR Conf: <span className="text-slate-300">{(field.ocr_confidence * 100).toFixed(0)}%</span>
                      </div>
                    )}
                  </td>
                  <td className="py-2.5 px-4 text-right font-sans">
                    <button
                      className={`p-1 rounded text-slate-400 hover:text-sky-300 ${
                        isSelected ? 'text-sky-400 bg-sky-500/20' : ''
                      }`}
                    >
                      <Eye className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
