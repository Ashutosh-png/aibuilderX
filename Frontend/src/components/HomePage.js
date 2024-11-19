import React, { useState } from 'react';
import axios from 'axios';
import './HomePage.css';
import { useNavigate } from 'react-router-dom'; // Import useNavigate


const HomePage = () => {
    const [prompt, setPrompt] = useState('');
    const [backendLanguage, setBackendLanguage] = useState('');
    const [fileUrl, setFileUrl] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const backendLanguages = [
        { label: "Python", value: "python" },
        { label: "Node.js", value: "node.js" },
        { label: "Ruby", value: "ruby" },
        { label: "Java", value: "java" },
        { label: "PHP", value: "php" },
        { label: "Go", value: "go" },
    ];

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            const response = await axios.post('https://api.aibuilderx.com/generate_code', 
                {
                    prompt, 
                    backend_language: backendLanguage 
                },
                { 
                    responseType: 'blob' 
                });
            const url = window.URL.createObjectURL(new Blob([response.data]));
            setFileUrl(url);
        } catch (error) {
            console.error('Error generating code', error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="homepage">
            <h1 className="site-title">AI Project Builder</h1>
            <button onClick={() => navigate('/ComicGenerator')} className="button">
                Go to Comic Generator
            </button>
            <div className="container">
                {/* <h1 className="heading">Generate Your Project</h1> */}
                <form onSubmit={handleSubmit} className="form">
                    <div className="form-group">
                        <label htmlFor="language" className="label">Select Backend Language</label>
                        <select 
                            id="language" 
                            value={backendLanguage} 
                            placeholder="Describe your project..." 
                            onChange={(e) => setBackendLanguage(e.target.value)} 
                            className="form-control"
                        >
                            <option value="">Select a language</option>
                            {backendLanguages.map((lang) => (
                                <option key={lang.value} value={lang.value}>{lang.label}</option>
                            ))}
                        </select>
                    </div>
                    <div className="form-group">
                      
                        <textarea 
                            id="prompt" 
                            placeholder="Describe your project..." 
                            value={prompt} 
                            onChange={(e) => setPrompt(e.target.value)} 
                            className="form-control textarea" 
                            rows="5" 
                        />
                    </div>
                    <div className="button-container">
                        <button type="submit" className="button" disabled={loading}>
                            {loading ? 'Creating...' : 'Create Project'}
                        </button>
                    </div>
                </form>
                {loading && (
                    <div className="loading-bar">
                        <div className="loading-bar-inner"></div>
                    </div>
                )}
                {fileUrl && (
                    <div className="download-container">
                        <a href={fileUrl} download="generated_code.zip" className="download-button">Download Project Files</a>
                    </div>
                )}
            </div>
        </div>
    );
};

export default HomePage;