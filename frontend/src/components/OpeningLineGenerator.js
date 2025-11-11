import React from 'react';

function OpeningLineGenerator({ openingLines, onSelectLine }) {
  return (
    <div className="bg-white rounded-2xl shadow-2xl p-8">
      <h2 className="text-3xl font-bold text-center mb-6 text-transparent bg-clip-text bg-gradient-to-r from-pink-500 to-purple-500">
        Your Opening Lines
      </h2>
      <p className="text-center text-gray-600 mb-8">
        Click on your favorite to celebrate! 🎉
      </p>
      
      <div className="space-y-6">
        {openingLines.map((line, index) => (
          <div
            key={index}
            onClick={onSelectLine}
            className="group relative p-6 border-2 border-gray-200 rounded-xl hover:border-purple-500 hover:shadow-xl transition-all cursor-pointer transform hover:scale-102"
          >
            <div className="flex items-start space-x-4">
              <div className="flex-shrink-0">
                <div className="w-12 h-12 bg-gradient-to-r from-pink-500 via-purple-500 to-blue-500 rounded-full flex items-center justify-center text-white font-bold text-xl">
                  {index + 1}
                </div>
              </div>
              <div className="flex-1">
                <p className="text-lg text-gray-800 leading-relaxed group-hover:text-purple-700 transition-colors">
                  {line.text}
                </p>
                <div className="mt-3 flex items-center space-x-4 text-sm text-gray-500">
                  <span className="flex items-center">
                    🌡️ Temperature: {line.temperature}
                  </span>
                  <span className="flex items-center">
                    🎯 Max Tokens: {line.max_tokens}
                  </span>
                </div>
              </div>
            </div>
            
            <div className="absolute top-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity">
              <span className="text-2xl">👆</span>
            </div>
          </div>
        ))}
      </div>
      
      <div className="mt-8 text-center text-sm text-gray-500">
        <p>💡 Tip: Each line is generated with different AI parameters for variety!</p>
      </div>
    </div>
  );
}

export default OpeningLineGenerator;
