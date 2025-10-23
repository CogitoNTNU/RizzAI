import React, { useState } from 'react';
import ImageUpload from './components/ImageUpload';
import OpeningLineGenerator from './components/OpeningLineGenerator';
import KissAnimation from './components/KissAnimation';

function App() {
  const [image, setImage] = useState(null);
  const [description, setDescription] = useState('');
  const [openingLines, setOpeningLines] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showKisses, setShowKisses] = useState(false);

  const handleImageUpload = (uploadedImage) => {
    setImage(uploadedImage);
  };

  const handleGenerateLines = async () => {
    if (!image || !description) {
      alert('Please upload an image and provide a description!');
      return;
    }

    setLoading(true);
    setOpeningLines([]);

    try {
      const formData = new FormData();
      formData.append('image', image);
      formData.append('description', description);

      const response = await fetch('http://localhost:8000/generate', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to generate opening lines');
      }

      const data = await response.json();
      setOpeningLines(data.opening_lines);
    } catch (error) {
      console.error('Error generating opening lines:', error);
      alert('Failed to generate opening lines. Make sure the backend server is running!');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectLine = () => {
    setShowKisses(true);
    setTimeout(() => setShowKisses(false), 3000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-100 via-purple-100 to-blue-100">
      {showKisses && <KissAnimation />}
      
      <div className="container mx-auto px-4 py-8">
        <header className="text-center mb-12">
          <h1 className="text-6xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-pink-500 via-purple-500 to-blue-500 mb-4">
            💘 RizzAI 💘
          </h1>
          <p className="text-xl text-gray-700">
            AI-Powered Opening Line Generator
          </p>
          <p className="text-sm text-gray-600 mt-2">
            Upload a photo, add a description, and let AI create the perfect opening line!
          </p>
        </header>

        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-2xl shadow-2xl p-8 mb-8">
            <ImageUpload onImageUpload={handleImageUpload} />

            <div className="mt-6">
              <label className="block text-lg font-semibold text-gray-700 mb-2">
                Profile Description
              </label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Describe the person... (e.g., Her name is Sarah. 25 kilometers away. Loves hiking and photography. Has a dog. Drinks socially on weekends.)"
                className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-purple-500 focus:outline-none transition-colors resize-none"
                rows="4"
              />
            </div>

            <button
              onClick={handleGenerateLines}
              disabled={loading || !image || !description}
              className="w-full mt-6 px-6 py-4 bg-gradient-to-r from-pink-500 via-purple-500 to-blue-500 text-white font-bold text-lg rounded-lg hover:shadow-lg transform hover:scale-105 transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
            >
              {loading ? (
                <span className="flex items-center justify-center">
                  <svg className="animate-spin h-6 w-6 mr-3" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Generating Magic...
                </span>
              ) : (
                '✨ Generate Opening Lines ✨'
              )}
            </button>
          </div>

          {openingLines.length > 0 && (
            <OpeningLineGenerator 
              openingLines={openingLines} 
              onSelectLine={handleSelectLine}
            />
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
