import React, { useState } from "react";
import { useForm } from "react-hook-form";
import { Upload, FileText, Send } from "lucide-react";

interface InputFormProps {
  onSubmit: (data: { audioUrl?: string; textInput?: string }) => void;
  isLoading: boolean;
}

interface FormData {
  audioUrl: string;
  textInput: string;
}

export const InputForm: React.FC<InputFormProps> = ({
  onSubmit,
  isLoading = false,
}) => {
  const [inputType, setInputType] = useState<"audio" | "text">("audio");
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormData>();

  const handleFormSubmit = (data: FormData) => {
    const submitData =
      inputType === "audio"
        ? { audioUrl: data.audioUrl }
        : { textInput: data.textInput };

    onSubmit(submitData);    
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      {/* Input Type Toggle */}
      <p className="text-sm text-gray-500 text-center mb-4">
        Select the input type:
      </p>
      <div className="flex justify-center space-x-4 mb-6">
        <button
          type="button"
          onClick={() => setInputType("audio")}
          className={`flex items-center space-x-2 px-4 py-2 rounded-full transition-colors cursor-pointer ${
            inputType === "audio"
              ? "bg-[#657bfa] text-white"
              : "bg-gray-100 text-gray-600 hover:bg-gray-200"
          }`}
        >
          <Upload size={15} />
          <span>Audio File</span>
        </button>
        <button
          type="button"
          onClick={() => setInputType("text")}
          className={`flex items-center space-x-2 px-4 py-2 rounded-full transition-colors cursor-pointer ${
            inputType === "text"
              ? "bg-[#657bfa] text-white"
              : "bg-gray-100 text-gray-600 hover:bg-gray-200"
          }`}
        >
          <FileText size={15} />
          <span>Text Input</span>
        </button>
      </div>

      <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-4">
        {inputType === "audio" ? (
          <div>
            <label
              htmlFor="audioUrl"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              Audio File URL
            </label>
            <input
              {...register("audioUrl", {
                required: "Audio URL is required",
                pattern: {
                  value: /^https?:\/\/.+/,
                  message: "Please enter a valid URL",
                },
              })}
              type="url"
              id="audioUrl"
              placeholder="https://example.com/audio-file.mp3"
              disabled={isLoading}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            {errors.audioUrl && (
              <p className="text-red-500 text-sm mt-1">
                {errors.audioUrl.message}
              </p>
            )}
            <p className="text-sm text-gray-500 mt-1">
              Provide a direct link to an audio file (MP3, WAV, etc.)
            </p>
          </div>
        ) : (
          <div>
            <label
              htmlFor="textInput"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              Medical Text Input
            </label>
            <textarea
              {...register("textInput", {
                required: "Text input is required",
                minLength: {
                  value: 10,
                  message: "Please enter at least 10 characters",
                },
              })}
              id="textInput"
              rows={6}
              placeholder="Enter patient symptoms, medical history, or consultation notes..."
              disabled={isLoading}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-vertical"
            />
            {errors.textInput && (
              <p className="text-red-500 text-sm mt-1">
                {errors.textInput.message}
              </p>
            )}
            <p className="text-sm text-gray-500 mt-1">
              Describe symptoms, patient information, or reason for visit
            </p>
          </div>
        )}

        <div className="flex justify-center mt-10">
          <button
            type="submit"
            disabled={isLoading}
            className=" bg-[#657bfa] text-white py-3 px-4 rounded-full hover:bg-[#657bfa]/80 disabled:opacity-50 cursor-pointer disabled:cursor-not-allowed flex items-center justify-center space-x-2"
          >
            {isLoading ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                <span>Processing...</span>
              </>
            ) : (
              <>
                <Send size={15} />
                <span>Process Medical Information</span>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};
