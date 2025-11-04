// About page component
import { Link } from 'react-router-dom';

const About: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <Link to="/" className="text-2xl font-bold text-blue-600">
              ParkinsonCare
            </Link>
            <div className="space-x-4">
              <Link
                to="/login"
                className="text-gray-600 hover:text-blue-600 font-medium"
              >
                Login
              </Link>
              <Link
                to="/register"
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 font-medium"
              >
                Get Started
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="max-w-4xl mx-auto">
          {/* Hero Section */}
          <div className="text-center mb-16">
            <h1 className="text-4xl font-bold text-gray-900 mb-6">
              About ParkinsonCare
            </h1>
            <p className="text-xl text-gray-600 leading-relaxed">
              Empowering healthcare professionals and patients with advanced AI-driven 
              Parkinson's disease detection and monitoring solutions.
            </p>
          </div>

          {/* Mission Section */}
          <div className="mb-16">
            <h2 className="text-3xl font-bold text-gray-900 mb-6">Our Mission</h2>
            <p className="text-lg text-gray-700 leading-relaxed mb-6">
              ParkinsonCare is dedicated to revolutionizing the early detection and ongoing 
              management of Parkinson's disease through cutting-edge artificial intelligence 
              and machine learning technologies. We believe that early, accurate diagnosis 
              can significantly improve patient outcomes and quality of life.
            </p>
            <p className="text-lg text-gray-700 leading-relaxed">
              Our platform bridges the gap between advanced medical technology and practical 
              healthcare delivery, making sophisticated diagnostic tools accessible to 
              healthcare providers worldwide.
            </p>
          </div>

          {/* Features Section */}
          <div className="mb-16">
            <h2 className="text-3xl font-bold text-gray-900 mb-8">Key Features</h2>
            <div className="grid md:grid-cols-2 gap-8">
              <div className="bg-white p-6 rounded-lg shadow-md">
                <div className="flex items-center mb-4">
                  <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mr-4">
                    <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900">AI-Powered Analysis</h3>
                </div>
                <p className="text-gray-600">
                  Advanced machine learning algorithms analyze voice patterns, motor symptoms, 
                  and other biomarkers to detect early signs of Parkinson's disease.
                </p>
              </div>

              <div className="bg-white p-6 rounded-lg shadow-md">
                <div className="flex items-center mb-4">
                  <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mr-4">
                    <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900">Clinical Validation</h3>
                </div>
                <p className="text-gray-600">
                  Our algorithms are trained on clinically validated datasets and continuously 
                  refined based on real-world healthcare outcomes.
                </p>
              </div>

              <div className="bg-white p-6 rounded-lg shadow-md">
                <div className="flex items-center mb-4">
                  <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mr-4">
                    <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
                    </svg>
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900">Patient-Centered Care</h3>
                </div>
                <p className="text-gray-600">
                  Intuitive interfaces for both patients and healthcare providers, with 
                  comprehensive tracking and monitoring capabilities.
                </p>
              </div>

              <div className="bg-white p-6 rounded-lg shadow-md">
                <div className="flex items-center mb-4">
                  <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center mr-4">
                    <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                    </svg>
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900">Secure & Private</h3>
                </div>
                <p className="text-gray-600">
                  Built with healthcare-grade security standards, ensuring patient data 
                  privacy and compliance with medical regulations.
                </p>
              </div>
            </div>
          </div>

          {/* Technology Section */}
          <div className="mb-16">
            <h2 className="text-3xl font-bold text-gray-900 mb-6">Our Technology</h2>
            <div className="bg-white p-8 rounded-lg shadow-md">
              <p className="text-lg text-gray-700 leading-relaxed mb-6">
                ParkinsonCare leverages state-of-the-art machine learning techniques including:
              </p>
              <ul className="grid md:grid-cols-2 gap-4 text-gray-700">
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-blue-600 rounded-full mr-3"></span>
                  Deep Neural Networks for voice analysis
                </li>
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-blue-600 rounded-full mr-3"></span>
                  Computer Vision for motor symptom detection
                </li>
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-blue-600 rounded-full mr-3"></span>
                  Natural Language Processing for medical records
                </li>
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-blue-600 rounded-full mr-3"></span>
                  Ensemble methods for improved accuracy
                </li>
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-blue-600 rounded-full mr-3"></span>
                  Real-time data processing and analysis
                </li>
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-blue-600 rounded-full mr-3"></span>
                  Cloud-based scalable infrastructure
                </li>
              </ul>
            </div>
          </div>

          {/* Team Section */}
          <div className="mb-16">
            <h2 className="text-3xl font-bold text-gray-900 mb-6">Our Commitment</h2>
            <p className="text-lg text-gray-700 leading-relaxed mb-6">
              We are committed to advancing the field of neurological healthcare through 
              innovation, research, and collaboration with medical professionals worldwide. 
              Our team combines expertise in artificial intelligence, healthcare technology, 
              and clinical research to deliver solutions that make a real difference in 
              patients' lives.
            </p>
            <p className="text-lg text-gray-700 leading-relaxed">
              By partnering with healthcare providers, researchers, and patient advocacy 
              groups, we ensure that our technology serves the real needs of the medical 
              community and the patients they care for.
            </p>
          </div>

          {/* CTA Section */}
          <div className="text-center bg-blue-50 p-8 rounded-lg">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              Ready to Get Started?
            </h2>
            <p className="text-lg text-gray-600 mb-6">
              Join healthcare professionals who are already using ParkinsonCare to 
              improve patient outcomes.
            </p>
            <div className="space-x-4">
              <Link
                to="/register"
                className="bg-blue-600 text-white px-8 py-3 rounded-lg hover:bg-blue-700 font-medium inline-block"
              >
                Get Started Today
              </Link>
              <Link
                to="/"
                className="bg-white text-blue-600 px-8 py-3 rounded-lg hover:bg-gray-50 font-medium inline-block border border-blue-600"
              >
                Back to Home
              </Link>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default About;