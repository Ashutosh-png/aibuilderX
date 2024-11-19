// src/ImageGenerator.js
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './ImageGenerator.css';

const ImageGenerator = () => {
    const [prompt, setPrompt] = useState('');
    const [images, setImages] = useState([]);
    const [error, setError] = useState('');
    const [fetchingImages, setFetchingImages] = useState(false);

    const handlePromptChange = (e) => {
        setPrompt(e.target.value);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setImages([]);
        setFetchingImages(true); // Start fetching images after generating

        try {
            const response = await axios.post('https://api.aibuilderx.com/generate-images', {
                prompt: prompt.trim()
            });
            setImages(response.data.images);
        } catch (err) {
            setError('Failed to generate images. Please try again.');
            console.error(err);
        }
    };

    useEffect(() => {
        const fetchImages = async () => {
            try {
                const response = await axios.get('https://api.aibuilderx.com/images');
                if (response.data.images) {
                    setImages(response.data.images);
                } else if (response.data.message) {
                    console.log(response.data.message); // Log the message
                    setFetchingImages(false); // Stop fetching if no images are available
                }
            } catch (err) {
                console.error('Failed to fetch images:', err);
            }
        };

        if (fetchingImages) {
            const intervalId = setInterval(fetchImages, 4000); // Fetch images every 4 seconds
            return () => clearInterval(intervalId); // Cleanup on unmount
        }
    }, [fetchingImages]); // Depend on fetchingImages state

    return (
        <div>
            <h1>Comic Story Generator</h1>
            <form onSubmit={handleSubmit}>
                <input
                    type="text"
                    value={prompt}
                    onChange={handlePromptChange}
                    placeholder="Enter your prompt"
                />
                <button type="submit">Generate your comic</button>
            </form>
            {error && <p style={{ color: 'red' }}>{error}</p>}
            {fetchingImages && images.length <1 && (
                <p>Loading images, please wait...</p> // Loading message
            )}
            <div>
                {images.length > 0 && <h2>Generated Story</h2>}
                {images.map((image, index) => (
                    <img key={index} src={`data:image/jpeg;base64,${image}`} alt={`Generated ${index}`} style={{ width: '300px', margin: '10px' }} />
                ))}
            </div>
        </div>
    );
};

export default ImageGenerator;