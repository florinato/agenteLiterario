import SimpleMDE from 'easymde';
import React, { useCallback, useEffect, useRef, useState } from 'react';
import "simplemde/dist/simplemde.min.css";

function EditorCanvas({ filePath, content, onSave }) {
  const [value, setValue] = useState(content || '');
  const [isDarkMode, setIsDarkMode] = useState(false);
  const editorRef = useRef(null);
  const simpleMDERef = useRef(null);

  useEffect(() => {
    // Initialize editor
    simpleMDERef.current = new SimpleMDE({
      element: editorRef.current,
      initialValue: value,
      autofocus: false,
      spellChecker: false,
      forceSync: true,
      styleSelectedText: false,
    });

    const cm = simpleMDERef.current.codemirror;
    if (!isDarkMode) {
      cm.setOption("theme", "default");
    } else {
      cm.setOption("theme", "material");
    }

    return () => {
      // Cleanup
      if (simpleMDERef.current) {
        simpleMDERef.current.toTextArea();
        simpleMDERef.current = null;
      }
    };
  }, []);

  useEffect(() => {
    const cm = simpleMDERef.current.codemirror;
    if (!isDarkMode) {
      cm.setOption("theme", "default");
      cm.getWrapperElement().style.backgroundColor = "#fff";
      cm.getScrollerElement().style.backgroundColor = "#fff";
      cm.getScrollerElement().style.color = "#000";
      document.body.classList.add('light-mode');
    } else {
      cm.setOption("theme", "material");
      cm.getWrapperElement().style.backgroundColor = "#333";
      cm.getScrollerElement().style.backgroundColor = "#333";
      cm.getScrollerElement().style.color = "#fff";
      document.body.classList.remove('light-mode');
    }
  }, [isDarkMode]);

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

  const toggleDarkMode = () => {
    setIsDarkMode(!isDarkMode);
    const cm = simpleMDERef.current.codemirror;
    if (!isDarkMode) {
      cm.setOption("theme", "material");
      cm.getWrapperElement().style.backgroundColor = "#333";
      cm.getScrollerElement().style.backgroundColor = "#333";
      cm.getScrollerElement().style.color = "#fff";
      document.body.classList.remove('light-mode');
    } else {
      cm.setOption("theme", "default");
      cm.getWrapperElement().style.backgroundColor = "#fff";
      cm.getScrollerElement().style.backgroundColor = "#fff";
      cm.getScrollerElement().style.color = "#000";
      document.body.classList.add('light-mode');
    }
  };

  return (
    <div className="editor-canvas" style={{ 
      padding: '10px',
      backgroundColor: 'var(--bg-color)',
      color: 'var(--text-color)'
    }}>
      <textarea ref={editorRef} style={{backgroundColor: 'var(--bg-color)', color: 'var(--text-color)'}}/>
      <button onClick={handleSave} style={{ marginTop: '10px' }}>Save</button>
      <button onClick={toggleDarkMode} style={{ marginTop: '10px' }}>
        {isDarkMode ? 'Light Mode' : 'Dark Mode'}
      </button>
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
