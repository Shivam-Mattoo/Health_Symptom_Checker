import { useState } from 'react';
import ApiService from '../services/api';

function SymptomForm({ onAnalysisComplete }) {
  const [symptoms, setSymptoms] = useState('');
  const [loading, setLoading] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState('');
  const [error, setError] = useState(null);
  const [inputType, setInputType] = useState('text'); // 'text', 'image', 'pdf'
  const [selectedFile, setSelectedFile] = useState(null);
  const [pdfUploaded, setPdfUploaded] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
      if (inputType === 'text' && !symptoms.trim()) {
        setError('Please enter your symptoms');
        return;
      }

      if (inputType === 'image' && !selectedFile) {
        setError('Please select an image file');
        return;
      }

      if (inputType === 'pdf') {
        if (!selectedFile && !pdfUploaded) {
          setError('Please select a PDF file to upload');
          return;
        }
        if (!pdfUploaded && selectedFile) {
          setLoading(true);
          setLoadingMessage('Uploading PDF and extracting text...');
          setUploadProgress(30);
          try {
            // First upload the PDF
            await ApiService.uploadPDF(selectedFile);
            setPdfUploaded(true);
            setUploadProgress(100);
            setLoadingMessage('PDF uploaded successfully!');
            setTimeout(() => {
              setLoading(false);
              setLoadingMessage('');
              setUploadProgress(0);
            }, 1000);
            return; // Don't analyze yet, wait for user to enter symptoms
          } catch (err) {
            setError(err.message || 'Failed to upload PDF');
            setLoading(false);
            setLoadingMessage('');
            setUploadProgress(0);
            return;
          }
        }
        if (pdfUploaded && !symptoms.trim()) {
          setError('Please enter symptoms to analyze with the uploaded PDF');
          return;
        }
      }

    setLoading(true);
    setError(null);
    setUploadProgress(0);

    try {
      let result;
      
      if (inputType === 'text') {
        setLoadingMessage('🔍 Analyzing your symptoms...');
        setUploadProgress(25);
        setTimeout(() => setUploadProgress(50), 500);
        result = await ApiService.analyzeSymptoms(symptoms);
        setUploadProgress(100);
      } else if (inputType === 'image') {
        setLoadingMessage('📸 Processing image...');
        setUploadProgress(30);
        result = await ApiService.analyzeImage(selectedFile, symptoms);
        setUploadProgress(100);
      } else if (inputType === 'pdf' && pdfUploaded) {
        setLoadingMessage('📄 Searching PDF knowledge base...');
        setUploadProgress(30);
        setTimeout(() => setUploadProgress(60), 500);
        // Analyze symptoms with PDF RAG
        result = await ApiService.analyzeWithPDF(symptoms);
        setUploadProgress(100);
      }
      
      setLoadingMessage('✅ Analysis complete!');
      setTimeout(() => {
        onAnalysisComplete(result);
        setSymptoms('');
        setSelectedFile(null);
        setPdfUploaded(false);
        setLoadingMessage('');
        setUploadProgress(0);
      }, 500);
    } catch (err) {
      setError(err.message || `Failed to analyze ${inputType}. Please try again.`);
      setLoadingMessage('');
      setUploadProgress(0);
    } finally {
      setTimeout(() => setLoading(false), 600);
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (inputType === 'image' && !file.type.startsWith('image/')) {
        setError('Please select a valid image file');
        return;
      }
      if (inputType === 'pdf' && file.type !== 'application/pdf') {
        setError('Please select a valid PDF file');
        return;
      }
      setSelectedFile(file);
      setError(null);
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto animate-fade-in">
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Input Type Selection with Modern Cards */}
        <div className="grid grid-cols-3 gap-4 mb-8">
          <button
            type="button"
            onClick={() => {
              setInputType('text');
              setSelectedFile(null);
              setPdfUploaded(false);
            }}
            className={`group relative p-6 rounded-2xl font-semibold transition-all duration-300 transform hover:scale-105 ${
              inputType === 'text'
                ? 'bg-linear-to-br from-blue-500 to-purple-600 text-white shadow-2xl'
                : 'bg-white/80 backdrop-blur-lg text-gray-700 hover:shadow-xl border border-gray-200'
            }`}
          >
            <div className="flex flex-col items-center space-y-3">
              <svg className={`w-8 h-8 ${inputType === 'text' ? 'text-white' : 'text-blue-500'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
              <span>Text Input</span>
            </div>
            {inputType === 'text' && (
              <div className="absolute inset-0 rounded-2xl bg-white/20 animate-pulse"></div>
            )}
          </button>
          
          <button
            type="button"
            onClick={() => {
              setInputType('image');
              setSelectedFile(null);
              setPdfUploaded(false);
            }}
            className={`group relative p-6 rounded-2xl font-semibold transition-all duration-300 transform hover:scale-105 ${
              inputType === 'image'
                ? 'bg-linear-to-br from-purple-500 to-pink-600 text-white shadow-2xl'
                : 'bg-white/80 backdrop-blur-lg text-gray-700 hover:shadow-xl border border-gray-200'
            }`}
          >
            <div className="flex flex-col items-center space-y-3">
              <svg className={`w-8 h-8 ${inputType === 'image' ? 'text-white' : 'text-purple-500'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <span>Image Upload</span>
            </div>
            {inputType === 'image' && (
              <div className="absolute inset-0 rounded-2xl bg-white/20 animate-pulse"></div>
            )}
          </button>
          
          <button
            type="button"
            onClick={() => {
              setInputType('pdf');
              setSelectedFile(null);
              setPdfUploaded(false);
            }}
            className={`group relative p-6 rounded-2xl font-semibold transition-all duration-300 transform hover:scale-105 ${
              inputType === 'pdf'
                ? 'bg-linear-to-br from-pink-500 to-rose-600 text-white shadow-2xl'
                : 'bg-white/80 backdrop-blur-lg text-gray-700 hover:shadow-xl border border-gray-200'
            }`}
          >
            <div className="flex flex-col items-center space-y-3">
              <svg className={`w-8 h-8 ${inputType === 'pdf' ? 'text-white' : 'text-pink-500'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
              </svg>
              <span>PDF Document</span>
            </div>
            {inputType === 'pdf' && (
              <div className="absolute inset-0 rounded-2xl bg-white/20 animate-pulse"></div>
            )}
          </button>
        </div>

        {/* Text Input */}
        {inputType === 'text' && (
          <div>
            <label 
              htmlFor="symptoms" 
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              Describe your symptoms
            </label>
            <textarea
              id="symptoms"
              value={symptoms}
              onChange={(e) => setSymptoms(e.target.value)}
              placeholder="e.g., I have been experiencing headaches, fever, and fatigue for the past 3 days..."
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              rows="6"
              disabled={loading}
            />
          </div>
        )}

        {/* Image Input */}
        {inputType === 'image' && (
          <div className="space-y-4">
            <div>
              <label 
                htmlFor="image" 
                className="block text-sm font-medium text-gray-700 mb-2"
              >
                Upload Medical Image
              </label>
              <input
                id="image"
                type="file"
                accept="image/*"
                onChange={handleFileChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                disabled={loading}
              />
              {selectedFile && (
                <p className="mt-2 text-sm text-gray-600">
                  Selected: {selectedFile.name} ({(selectedFile.size / 1024).toFixed(2)} KB)
                </p>
              )}
            </div>
            <div>
              <label 
                htmlFor="image-symptoms" 
                className="block text-sm font-medium text-gray-700 mb-2"
              >
                Additional Symptoms Description (Optional)
              </label>
              <textarea
                id="image-symptoms"
                value={symptoms}
                onChange={(e) => setSymptoms(e.target.value)}
                placeholder="Describe any additional symptoms or context..."
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                rows="4"
                disabled={loading}
              />
            </div>
          </div>
        )}

        {/* PDF Input */}
        {inputType === 'pdf' && (
          <div className="space-y-4">
            <div>
              <label 
                htmlFor="pdf" 
                className="block text-sm font-medium text-gray-700 mb-2"
              >
                Upload Medical PDF Document
              </label>
              <input
                id="pdf"
                type="file"
                accept="application/pdf"
                onChange={handleFileChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                disabled={loading || pdfUploaded}
              />
              {selectedFile && (
                <p className="mt-2 text-sm text-gray-600">
                  Selected: {selectedFile.name} ({(selectedFile.size / 1024).toFixed(2)} KB)
                </p>
              )}
              {pdfUploaded && (
                <p className="mt-2 text-sm text-green-600 font-medium">
                  ✓ PDF uploaded successfully! Now enter symptoms to analyze with PDF content.
                </p>
              )}
            </div>
            <div>
              <label 
                htmlFor="pdf-symptoms" 
                className="block text-sm font-medium text-gray-700 mb-2"
              >
                Describe your symptoms (will be analyzed using PDF content)
              </label>
              <textarea
                id="pdf-symptoms"
                value={symptoms}
                onChange={(e) => setSymptoms(e.target.value)}
                placeholder="e.g., I have been experiencing headaches, fever, and fatigue..."
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                rows="6"
                disabled={loading}
              />
            </div>
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-start">
            <svg className="w-5 h-5 mr-2 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
            <span>{error}</span>
          </div>
        )}

        {loading && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-center justify-between mb-3">
              <span className="text-blue-800 font-medium">{loadingMessage}</span>
              <span className="text-blue-600 text-sm font-semibold">{uploadProgress}%</span>
            </div>
            <div className="w-full bg-blue-200 rounded-full h-2.5 overflow-hidden">
              <div 
                className="bg-blue-600 h-2.5 rounded-full transition-all duration-500 ease-out"
                style={{ width: `${uploadProgress}%` }}
              >
                <div className="h-full w-full bg-gradient-to-r from-transparent via-white to-transparent opacity-30 animate-pulse"></div>
              </div>
            </div>
            <div className="flex items-center justify-center mt-3">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
              <span className="ml-3 text-sm text-blue-700">Please wait...</span>
            </div>
          </div>
        )}

        <button
          type="submit"
          disabled={loading || (inputType === 'text' && !symptoms.trim()) || 
                   ((inputType === 'image' || inputType === 'pdf') && !selectedFile) ||
                   (inputType === 'pdf' && !pdfUploaded && !symptoms.trim())}
          className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-all duration-200 transform hover:scale-[1.02] active:scale-[0.98] flex items-center justify-center"
        >
          {loading ? (
            <>
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Processing...
            </>
          ) : (
            <>
              {inputType === 'pdf' && !pdfUploaded ? (
                <>
                  <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                  Upload PDF
                </>
              ) : (
                <>
                  <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                  </svg>
                  Analyze Symptoms
                </>
              )}
            </>
          )}
        </button>
      </form>
    </div>
  );
}

export default SymptomForm;
