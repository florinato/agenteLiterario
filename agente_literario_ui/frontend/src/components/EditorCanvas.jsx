import SimpleMDE from 'easymde';
import React, { useCallback, useEffect, useRef, useState } from 'react';
import "simplemde/dist/simplemde.min.css";

function EditorCanvas({ filePath, content, onSave }) {
  const [value, setValue] = useState(content || '');
  const editorRef = useRef(null);
  const simpleMDERef = useRef(null);

  useEffect(() => {
    // Initialize editor
    simpleMDERef.current = new SimpleMDE({
      element: editorRef.current,
      initialValue: value,
      autofocus: false,
      spellChecker: false,
      forceSync: true
    });

    // Handle changes
    simpleMDERef.current.codemirror.on('change', () => {
      const newValue = simpleMDERef.current.value();
      setValue(newValue);
    });

    return () => {
      // Cleanup
      if (simpleMDERef.current) {
        simpleMDERef.current.toTextArea();
        simpleMDERef.current = null;
      }
    };
  }, []);

  useEffect(() => {
    // Update editor when content prop changes
    if (simpleMDERef.current && simpleMDERef.current.value() !== content) {
      simpleMDERef.current.value(content || '');
    }
  }, [content]);

  const handleSave = useCallback(() => {
    if (onSave) {
      onSave(filePath, value);
    }
  }, [filePath, value, onSave]);

  return (
    <div className="editor-canvas">
      <textarea ref={editorRef} />
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
