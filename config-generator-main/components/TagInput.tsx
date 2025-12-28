import React, { useState, KeyboardEvent, ChangeEvent, InputHTMLAttributes } from 'react';
import { X, Plus } from 'lucide-react';

interface TagInputProps {
  label: string;
  placeholder?: string;
  tags: string[];
  onChange: (newTags: string[]) => void;
  helperText?: string;
  transformValue?: (value: string) => string;
  inputProps?: InputHTMLAttributes<HTMLInputElement>;
}

const TagInput: React.FC<TagInputProps> = ({ 
  label, 
  placeholder = "Type and press Enter...", 
  tags, 
  onChange,
  helperText,
  transformValue,
  inputProps
}) => {
  const [inputValue, setInputValue] = useState('');

  const handleInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    let val = e.target.value;
    if (transformValue) {
      val = transformValue(val);
    }
    setInputValue(val);
  };

  const handleAddTag = () => {
    const trimmed = inputValue.trim();
    if (trimmed && !tags.includes(trimmed)) {
      onChange([...tags, trimmed]);
      setInputValue('');
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleAddTag();
    }
  };

  const removeTag = (indexToRemove: number) => {
    onChange(tags.filter((_, index) => index !== indexToRemove));
  };

  return (
    <div className="flex flex-col gap-2">
      <label className="text-sm font-medium text-slate-700">{label}</label>
      
      <div className="flex gap-2">
        <input
          type="text"
          className="flex-1 px-3 py-2 bg-white text-slate-900 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
          placeholder={placeholder}
          value={inputValue}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          {...inputProps}
        />
        <button
          type="button"
          onClick={handleAddTag}
          className="px-3 py-2 bg-slate-100 text-slate-600 rounded-lg hover:bg-slate-200 transition-colors"
        >
          <Plus size={18} />
        </button>
      </div>

      {helperText && <p className="text-xs text-slate-500">{helperText}</p>}

      {tags.length > 0 && (
        <div className="flex flex-wrap gap-2 mt-1">
          {tags.map((tag, index) => (
            <span 
              key={`${tag}-${index}`} 
              className="inline-flex items-center gap-1 px-2.5 py-1 bg-blue-50 text-blue-700 text-xs font-medium rounded-full border border-blue-100"
            >
              {tag}
              <button 
                type="button"
                onClick={() => removeTag(index)}
                className="hover:text-blue-900 focus:outline-none"
              >
                <X size={14} />
              </button>
            </span>
          ))}
        </div>
      )}
    </div>
  );
};

export default TagInput;