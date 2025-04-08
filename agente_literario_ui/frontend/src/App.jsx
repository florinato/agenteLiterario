import axios from 'axios';
import React, { useCallback, useEffect, useRef, useState } from 'react';
import './App.css'; // We'll add layout styles here
import EditorCanvas from './components/EditorCanvas';
import ErrorBoundary from './components/ErrorBoundary';
import FileExplorer from './components/FileExplorer';

const API_BASE_URL = 'http://localhost:8000'; // Ensure this matches FileExplorer

function App() {
  const [selectedFilePath, setSelectedFilePath] = useState(null);
  const [fileContent, setFileContent] = useState(''); // To display file content if agent returns it
  const [isLoadingContent, setIsLoadingContent] = useState(false); // Loading state for file content
  const [contentError, setContentError] = useState(null);
  const [agentResponse, setAgentResponse] = useState('');
  const [isAgentLoading, setIsAgentLoading] = useState(false); // Corrected setter name
  const [agentError, setAgentError] = useState(null); // Corrected setter name
  const [promptInput, setPromptInput] = useState('');
  const promptInputRef = useRef(null);

  // This function is kept in case we want the agent to read files and display content
  const handleFileSelect = useCallback(async (filePath) => {
    console.log("App received file select:", filePath);
    setSelectedFilePath(filePath); // Keep track of selected file for context
    setIsLoadingContent(true);
    setContentError(null);
    setAgentResponse(''); // Clear previous agent response
    setFileContent(''); // Clear previous content

    try {
      const response = await axios.get(`${API_BASE_URL}/api/files/read`, {
        params: { path: filePath }
      });
      setFileContent(response.data.content);
    } catch (err) {
      console.error("Error fetching file content:", err);
      setContentError(`Failed to load content for ${filePath}.`);
      setFileContent(''); // Clear content on error
    } finally {
      setIsLoadingContent(false);
    }
  }, []);

  useEffect(() => {
    // Focus on the prompt input when the component mounts
    if (promptInputRef.current) {
      promptInputRef.current.focus();
    }

    // Call handleFileSelect with agente_literario_features.md
    // handleFileSelect('agente_literario_features.md');
  }, [handleFileSelect]);

  const handleAgentPrompt = useCallback(async () => {
    if (!promptInput.trim()) {
      setAgentError("Please enter a prompt before sending.");
      return;
    }

    setIsAgentLoading(true); // Use correct setter
    setAgentError(null);
    setAgentResponse('');

    try {
      const response = await axios.post(
        `${API_BASE_URL}/api/agent/command`,
        {
          prompt: promptInput,
          file_path: selectedFilePath || "", // Pass the file path (might be null)
        }
      );
      setAgentResponse(response.data.response);
      console.log("Agent Response:", response.data.response);
    } catch (err) {
      console.error("Error running agent command:", err);
      setAgentError("Failed to run agent command."); // Use correct setter
      setAgentResponse('');
    } finally {
      setIsAgentLoading(false); // Use correct setter
    }
  }, [promptInput, selectedFilePath]);

  useEffect(() => {
    if (!selectedFilePath) {
      setAgentError("Please select a file before sending a prompt.");
      return;
    }
  }, [selectedFilePath]);// Removed fileContent dependency

  const handleInputChange = (event) => {
    setPromptInput(event.target.value);
  };

  const handleFileSave = useCallback(async (filePath, content) => {
    setIsAgentLoading(true);
    setAgentError(null);

    try {
      await axios.post(`${API_BASE_URL}/api/files/save`, {
        path: filePath,
        content: content,
      });
      setFileContent(content); // Update local state with saved content
      console.log("File saved successfully!");
    } catch (error) {
      console.error("Error saving file:", error);
      setAgentError("Failed to save file.");
    } finally {
      setIsAgentLoading(false);
    }
  }, []);

  try {
    return (
      <ErrorBoundary>
        <div className="app-container">
          {/* Sidebar might be used later to display file list returned by agent */}
          <aside className="sidebar">
            <FileExplorer onFileSelect={handleFileSelect} />
          </aside>
          <main className="main-content">
            {/* Use EditorCanvas to display and edit content */}
            <div className="editor-placeholder">
              <h2>Editor: {selectedFilePath || 'No file selected'}</h2>
              {isLoadingContent && <p>Loading content...</p>}
              {contentError && <p style={{ color: 'red' }}>{contentError}</p>}
              {!isLoadingContent && !contentError && (
                <EditorCanvas
                  filePath={selectedFilePath}
                  content={fileContent}
                  onSave={handleFileSave}
                />
              )}
            </div>
            {/* Response Area */}
            <div className="response-placeholder">
              <h3>Agent Response:</h3>
              {isAgentLoading && <p>Loading...</p>}
              {agentError && <p style={{ color: 'red' }}>{agentError}</p>}
              {/* Display agent response, which might include file content */}
              <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'monospace' }}>{agentResponse}</pre>
            </div>
            {/* Prompt Input */}
            <div className="prompt-placeholder">
              <input
                type="text"
                placeholder="Enter prompt for agent..."
                value={promptInput}
                onChange={handleInputChange}
                ref={promptInputRef}
              />
              <button onClick={handleAgentPrompt}>Send</button>
            </div>
          </main>
        </div>
      </ErrorBoundary>
    );
  } catch (error) {
    console.error("Error in App component:", error);
    return <div>Error loading application. See console for details.</div>;
  }
}

export default App;
