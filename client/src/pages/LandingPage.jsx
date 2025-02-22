import { useEffect } from "react";
import { GitlabIcon as GitHub, Linkedin, Mail, ArrowRight, Briefcase, Calendar, MapPin, Globe } from "lucide-react";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";

const features = [
  {
    name: "AI-Powered Communication",
    details: [
      "Seamless AI-driven messaging and collaboration",
      "Real-time language translation for global teams",
      "Smart email classification and prioritization",
      "Voice recognition for hands-free operation",
      "AI-powered sentiment analysis for better interactions",
    ],
  },
  {
    name: "Workflow Automation",
    details: [
      "Automate repetitive tasks with machine learning",
      "Smart scheduling and meeting coordination",
      "AI-driven document summarization and insights",
      "Intelligent task delegation based on workload analysis",
      "Workflow optimization for enhanced efficiency",
    ],
  },
  {
    name: "Data-Driven Insights",
    details: [
      "Real-time analytics for communication trends",
      "Predictive AI for workflow improvements",
      "Deep learning-based business intelligence",
      "AI-powered decision-making support",
      "Customizable AI dashboards for performance tracking",
    ],
  },
];



const CodePattern = () => (
  <svg
    className="absolute inset-0 w-full h-full opacity-5"
    xmlns="http://www.w3.org/2000/svg"
  >
    <pattern
      id="pattern-circles"
      x="0"
      y="0"
      width="50"
      height="50"
      patternUnits="userSpaceOnUse"
      patternContentUnits="userSpaceOnUse"
    >
      <circle id="pattern-circle" cx="10" cy="10" r="1.6" fill="#000"></circle>
    </pattern>
    <rect id="rect" x="0" y="0" width="100%" height="100%" fill="url(#pattern-circles)"></rect>
  </svg>
);

export default function Hero() {
  useEffect(() => {
    document.title = "AI-Powered Platform - Intelligent Communication & Workflow";
  }, []);

  const navigate = useNavigate();

  const handleGetStarted = () => {
    navigate("/sign-up"); 
  };

  const handleLogin = () => {
    navigate("/sign-up"); 
  };

  return (
    <section>
    <section
      id="hero"
      className="min-h-screen relative overflow-hidden bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 dark:from-gray-900 dark:via-indigo-900 dark:to-purple-900"
    >
      <div className="absolute inset-0 z-0">
        <CodePattern />
      </div>

      <div className="absolute inset-0 z-0 opacity-30">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-400 via-indigo-500 to-gray-800 animate-gradient-x"></div>
      </div>

      <div className="absolute top-6 right-6 gap-4 flex items-center z-10">
        <button
          onClick={handleLogin}
          className="px-5 py-2 bg-blue-800 hover:bg-blue-700  bg-gradient-to-r from-blue-700 to-gray-800 text-white rounded-full hover:from-blue-700 hover:to-purple-700 duration-300 hover:shadow-xl transition-all shadow-lg"
        >
          Login
        </button>
        <button
          onClick={handleGetStarted}
          className="px-5 py-2 bg-blue-600 text-white rounded-full hover:bg-blue-700 bg-gradient-to-r from-blue-600 to-gray-800 hover:from-blue-700 hover:to-purple-700 duration-300 hover:shadow-xl transition-all shadow-lg"
        >
          Sign In
        </button>
      </div>

      <div className="container mx-auto px-6 pt-32 pb-20 relative z-10">
        <div className="flex flex-col lg:flex-row items-center justify-between gap-12">
          <motion.div
            className="lg:w-1/2 text-center lg:text-left"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-6 bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-purple-600 dark:from-blue-400 dark:to-purple-400">
              FlowAI
            </h1>
            <h2 className="text-2xl md:text-3xl font-semibold mb-6 text-gray-700 dark:text-gray-300">
              Intelligent Communication & Workflow Enhancement
            </h2>
            <p className="text-lg md:text-xl text-gray-600 dark:text-gray-400 mb-8 max-w-2xl mx-auto lg:mx-0">
              Transforming productivity with cutting-edge AI. Streamline communication, optimize workflows, and enhance efficiency with intelligent automation and data-driven insights.
            </p>

           
            <motion.button
              
              onClick={handleGetStarted}
              className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-gray-800 text-white rounded-full hover:from-blue-700 hover:to-purple-700 transition-all duration-300 shadow-lg hover:shadow-xl"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              Get Started
              <ArrowRight className="w-4 h-4" />
            </motion.button>
          </motion.div>

          <motion.div
            className="lg:w-1/2"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            <div className="relative w-72 h-72 md:w-96 md:h-96 mx-auto">
              <img src="https://www.iconarchive.com/download/i138008/microsoft/fluentui-emoji-3d/Robot-3d.1024.png" alt="" />
              <div className="relative rounded-2xl overflow-hidden shadow-2xl">
                {/* <img
                  src=""
                  alt="Usman Zafar"
                  className="object-cover w-full h-full"
                /> */}
              </div>
            </div>
          </motion.div>
        </div>
      </div>

      <motion.div
        className="absolute bottom-10 left-1/2 transform -translate-x-1/2 flex flex-col items-center"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.8, duration: 0.6 }}
      >
        <div className="w-1 h-12 bg-gradient-to-b from-blue-600 to-purple-600 dark:from-blue-400 dark:to-purple-400 rounded-full animate-pulse"></div>
      </motion.div>
    </section>
    <section
      id="experience"
      className="py-20 bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-indigo-900 transition-colors duration-300 overflow-hidden relative"
    >
      <div className="container mx-auto px-6 relative z-10">
        <h2 className="text-4xl font-bold text-center text-gray-900 dark:text-white mb-12">
          AI-Powered Experience
        </h2>
        <div className="space-y-16">
          {features.map((exp, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 50 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: index * 0.2 }}
              className="bg-white dark:bg-gray-800 p-8 rounded-xl shadow-lg transition-all duration-300 hover:shadow-2xl relative overflow-hidden group"
            >
              <div className="relative z-10">
                <h3 className="text-2xl font-semibold mb-2 dark:text-white flex items-center">
                  <Globe className="w-6 h-6 mr-2 text-blue-500" /> {exp.name}
                </h3>
                {/* <p className="text-gray-600 dark:text-gray-300 mb-4 flex items-center">
                  <MapPin className="w-4 h-4 mr-2" /> {exp.location}
                </p>
                <p className="text-gray-600 dark:text-gray-300 mb-4 flex items-center">
                  <Calendar className="w-4 h-4 mr-2" /> {exp.period}
                </p> */}
                {/* <p className="text-xl font-medium mb-4 dark:text-gray-200 flex items-center">
                  <Briefcase className="w-5 h-5 mr-2" /> {exp.role}
                </p> */}
                <ul className="list-none space-y-2">
                  {exp.details.map((resp, idx) => (
                    <li key={idx} className="text-gray-700 dark:text-gray-300 flex items-start">
                      <span className="text-blue-500 mr-2">•</span>
                      {resp}
                    </li>
                  ))}
                </ul>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
    </section>
  );
}
