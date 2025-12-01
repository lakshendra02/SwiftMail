import React, { useEffect, useState } from "react";

const Login = () => {
  const [error, setError] = useState(null);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const authError = params.get("auth_error");
    if (authError) setError(authError);
  }, []);

  const handleLogin = () => {
    window.location.href = "http://localhost:8000/api/auth/login";
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100 px-4">
      <div className="bg-white p-10 rounded-2xl shadow-xl w-full max-w-md text-center border border-gray-200">
        <h1 className="text-3xl font-semibold mb-4 text-gray-800">
          SwiftMail - AI Email Assistant
        </h1>

        <p className="mb-6 text-gray-600">
          Log in with Google to access your email dashboard.
        </p>

        {error && (
          <div className="mb-5 p-3 bg-red-100 border border-red-300 text-red-700 text-sm rounded-lg">
            Login Error: {error}. Please try again.
          </div>
        )}

        <button
          onClick={handleLogin}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 rounded-xl transition shadow-md flex items-center justify-center space-x-3"
        >
          <svg
            className="w-6 h-6"
            viewBox="0 0 48 48"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              fill="#FFC107"
              d="M43.611 20.083H42V20H24v8h11.303c-1.63 4.347-5.874 7.55-10.42 7.55-6.759 0-12.263-5.403-12.263-12.075s5.504-12.075 12.263-12.075c3.344 0 6.447 1.37 8.784 3.593l5.803-5.698C37.042 3.12 30.675 0 24 0 10.745 0 0 10.745 0 24s10.745 24 24 24c12.115 0 20.31-8.2 20.31-23.953 0-1.346-.143-2.618-.387-3.87z"
            />
            <path
              fill="#FF3D00"
              d="M11.173 28.529c-1.344-1.996-2.127-4.305-2.127-6.792s.783-4.796 2.127-6.792l-5.804-5.698C3.12 11.234 0 17.276 0 24s3.12 12.766 5.369 17.062l5.804-5.533z"
            />
            <path
              fill="#4CAF50"
              d="M24 48c6.917 0 13.407-2.645 18.23-7.534l-6.222-4.92c-1.503 3.541-4.717 6.273-9.522 6.273-7.23 0-13.116-5.88-13.116-13.116s5.886-13.116 13.116-13.116c3.167 0 6.096 1.144 8.272 3.016l-1.018.995h-7.254v-6.52h14.509V24c0-1.127-.099-2.227-.312-3.32h-17.77V28h9.324c-.754 2.508-2.316 4.706-4.993 6.014-4.237 2.112-9.288 1.956-13.364-.473L5.368 41.062C9.287 44.912 16.2 48 24 48z"
            />
            <path
              fill="#1976D2"
              d="M43.611 20.083c0-1.29-.142-2.507-.387-3.674l-5.698-5.803c2.479 2.593 3.974 5.922 3.974 9.477s-1.495 6.884-3.974 9.477l5.698-5.803c.245-1.167.387-2.484.387-3.797z"
            />
          </svg>
          <span>Sign in with Google</span>
        </button>

        <p className="mt-6 text-xs text-gray-500 leading-relaxed">
          This app requires access to read, send, and delete your Gmail emails.
        </p>
      </div>
    </div>
  );
};

export default Login;
