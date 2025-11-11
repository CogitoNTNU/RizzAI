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
  const [configs, setConfigs] = useState([
    { max_new_tokens: 80, temperature: 0.9, do_sample: true, top_p: 0.9 },
    { max_new_tokens: 100, temperature: 1.2, do_sample: true, top_p: 0.9 },
    { max_new_tokens: 120, temperature: 1.5, do_sample: true, top_p: 0.9 },
  ]);

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
      formData.append('configs', JSON.stringify(configs));

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

  const addConfig = () => {
    setConfigs([...configs, { max_new_tokens: 100, temperature: 1.0, do_sample: true, top_p: 0.9 }]);
  };

  const removeConfig = (index) => {
    setConfigs(configs.filter((_, i) => i !== index));
  };

  const updateConfig = (index, key, value) => {
    const newConfigs = [...configs];
    // Convert to appropriate type
    if (key === 'do_sample') {
      newConfigs[index][key] = value === 'true' || value === true;
    } else if (key === 'max_new_tokens') {
      newConfigs[index][key] = parseInt(value) || 0;
    } else {
      newConfigs[index][key] = parseFloat(value) || 0;
    }
    setConfigs(newConfigs);
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

            <div className="mt-6">
              <div className="flex justify-between items-center mb-3">
                <label className="block text-lg font-semibold text-gray-700">
                  Generation Configurations
                </label>
                <button
                  onClick={addConfig}
                  className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors text-sm font-semibold"
                >
                  ➕ Add Config
                </button>
              </div>
              <p className="text-sm text-gray-600 mb-3">
                Configure parameters for model.generate(). Each config will generate one opening line.
              </p>
              
              <div className="space-y-4 max-h-96 overflow-y-auto">
                {configs.map((config, index) => (
                  <div key={index} className="p-4 border-2 border-gray-300 rounded-lg bg-gray-50">
                    <div className="flex justify-between items-center mb-3">
                      <h3 className="font-semibold text-gray-700">Config {index + 1}</h3>
                      {configs.length > 1 && (
                        <button
                          onClick={() => removeConfig(index)}
                          className="px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600 transition-colors text-sm"
                        >
                          Remove
                        </button>
                      )}
                    </div>
                    
                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Max New Tokens
                        </label>
                        <input
                          type="number"
                          value={config.max_new_tokens}
                          onChange={(e) => updateConfig(index, 'max_new_tokens', e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded focus:border-purple-500 focus:outline-none"
                        />
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Temperature
                        </label>
                        <input
                          type="number"
                          step="0.1"
                          value={config.temperature}
                          onChange={(e) => updateConfig(index, 'temperature', e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded focus:border-purple-500 focus:outline-none"
                        />
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Top P
                        </label>
                        <input
                          type="number"
                          step="0.1"
                          value={config.top_p}
                          onChange={(e) => updateConfig(index, 'top_p', e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded focus:border-purple-500 focus:outline-none"
                        />
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Do Sample
                        </label>
                        <select
                          value={config.do_sample ? 'true' : 'false'}
                          onChange={(e) => updateConfig(index, 'do_sample', e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded focus:border-purple-500 focus:outline-none"
                        >
                          <option value="true">True</option>
                          <option value="false">False</option>
                        </select>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
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
