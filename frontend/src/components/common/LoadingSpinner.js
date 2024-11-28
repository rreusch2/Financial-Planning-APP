import React from "react";
import { Loader } from "lucide-react";

const LoadingSpinner = ({ size = "default", className = "" }) => {
  const sizeClasses = {
    small: "h-4 w-4",
    default: "h-8 w-8",
    large: "h-12 w-12",
  };

  return (
    <div className="flex justify-center items-center min-h-[200px]">
      <Loader
        className={`animate-spin text-blue-500 ${sizeClasses[size]} ${className}`}
      />
    </div>
  );
};

export default LoadingSpinner;
