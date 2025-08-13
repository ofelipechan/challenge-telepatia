import { Brain } from "lucide-react";

function Header() {
  return (
    <header className="bg-white shadow-sm border-b">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-2">
              <Brain className="text-[#657bfa]" size={32} />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Telepatia</h1>
              <p className="text-sm text-gray-500">
                AI-Powered Medical Analysis
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <ul className="flex items-center space-x-4">
              <li>Home</li>
            </ul>
          </div>
        </div>
      </div>
    </header>
  );
}

export default Header;
