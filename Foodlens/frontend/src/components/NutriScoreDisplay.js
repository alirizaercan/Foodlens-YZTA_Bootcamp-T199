import React from 'react';

const NutriScoreDisplay = ({ grade, score, color, size = 'medium' }) => {
  const grades = ['A', 'B', 'C', 'D', 'E'];
  const colors = {
    'A': '#038141',
    'B': '#85BB2F', 
    'C': '#FECB00',
    'D': '#EE8100',
    'E': '#E63312'
  };

  const sizeClasses = {
    small: 'text-xs px-2 py-1',
    medium: 'text-sm px-3 py-2',
    large: 'text-lg px-4 py-3'
  };

  const containerSizeClasses = {
    small: 'text-sm',
    medium: 'text-base',
    large: 'text-xl'
  };

  if (!grade) return null;

  return (
    <div className={`flex items-center justify-center space-x-1 ${containerSizeClasses[size]}`}>
      {grades.map((g) => (
        <div
          key={g}
          className={`
            ${sizeClasses[size]}
            font-bold rounded transition-all duration-200
            ${g === grade 
              ? 'text-white transform scale-110 shadow-lg' 
              : 'text-gray-400 bg-gray-100'
            }
          `}
          style={g === grade ? { backgroundColor: colors[g] } : {}}
        >
          {g}
        </div>
      ))}
      
      {score !== undefined && size === 'large' && (
        <div className="ml-4 text-gray-600">
          <span className="text-sm">Score: </span>
          <span className="font-bold text-lg">{score}</span>
        </div>
      )}
    </div>
  );
};

export default NutriScoreDisplay;
