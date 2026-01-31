
import React, { useState } from 'react';

const SearchBar = ({ onSearch }) => {
  const [currentInput, setCurrentInput] = useState('');
  const [tags, setTags] = useState([]);

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      addTag();
    }
  };

  const addTag = () => {
    const trimmed = currentInput.trim().toUpperCase();
    if (trimmed && !tags.includes(trimmed)) {
      setTags([...tags, trimmed]);
      setCurrentInput('');
    }
  };

  const removeTag = (tagToRemove) => {
    setTags(tags.filter(tag => tag !== tagToRemove));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (tags.length > 0) {
      onSearch(tags);
    } else if (currentInput.trim()) {
        // If user typed something but didn't press enter to add tag, treat it as a search
        onSearch([currentInput.trim().toUpperCase()]);
    }
  };

  return (
    <div className="search-wrapper" style={{display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1rem'}}>
      <form className="search-container" onSubmit={handleSubmit} style={{marginBottom: '0'}}>
        <div className="input-group" style={{display: 'flex', gap: '0.5rem', alignItems: 'center'}}>
            <input
            type="text"
            placeholder="Enter symbol (e.g. AAPL) & Press Enter"
            value={currentInput}
            onChange={(e) => setCurrentInput(e.target.value)}
            onKeyDown={handleKeyDown}
            />
            <button type="button" onClick={addTag} style={{background: '#64748b'}}>Add</button>
            <button type="submit">Compare</button>
        </div>
      </form>
      
      {tags.length > 0 && (
          <div className="tags-container" style={{display: 'flex', gap: '0.5rem', flexWrap: 'wrap'}}>
            {tags.map(tag => (
                <span key={tag} style={{
                    background: '#e2e8f0', 
                    padding: '0.25rem 0.75rem', 
                    borderRadius: '1rem',
                    fontSize: '0.9rem',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem'
                }}>
                    {tag}
                    <button 
                        onClick={() => removeTag(tag)}
                        style={{
                            background: 'transparent', 
                            color: '#64748b', 
                            padding: 0, 
                            border: 'none', 
                            marginLeft: 0,
                            fontSize: '1rem',
                            cursor: 'pointer'
                        }}
                    >
                        ×
                    </button>
                </span>
            ))}
          </div>
      )}
    </div>
  );
};

export default SearchBar;

