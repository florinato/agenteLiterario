import React, { useCallback, useEffect, useState } from 'react';
import ReactSimpleMDE from 'react-simplemde-editor';
import "simplemde/dist/simplemde.min.css"; // Import the CSS

function EditorCanvas({ filePath, content, onSave }) {
  const [value, setValue] = useState(''); // Initialize state without content
  // Use useEffect to update the value when the content prop changes
  useEffect(() => {
    setValue(content || '');
  }, [content]);

  const handleChange = (newValue) => {
    setValue(newValue);
  };

  const handleSave = useCallback(() => {
    if (onSave) {
      onSave(filePath, value);
    }
  }, [filePath, value, onSave]);

  const options = {
    autofocus: false,
    spellChecker: false,
    // Add more SimpleMDE options here as needed
  };

  return (
    <div className="editor-canvas">
      <ReactSimpleMDE
        value={value}
        onChange={handleChange}
        options={options}
      />
      <button onClick={handleSave} style={{ marginTop: '10px' }}>Save</button>
    </div>
  );
}

// Add some basic styling
const styles = {
  editorCanvas: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
  },
  saveButton: {
    marginTop: '10px',
  }
};

export default EditorCanvas;
