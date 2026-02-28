import { Link } from "react-router-dom";
import {
  HeartIcon,
  CpuChipIcon,
  ShieldCheckIcon,
  UserGroupIcon,
  ChartBarIcon,
  BeakerIcon,
} from "@heroicons/react/24/outline";
import { motion, useScroll, useTransform } from "framer-motion";
import { memo } from "react";
import GradientText from "../components/common/GradientText";
import Antigravity from "../components/common/Antigravity";

// Extracted data following react-best-practices to prevent inline constant recreation
const FEATURES = [
  {
    title: "AI-Powered Analysis",
    description: "Advanced machine learning models analyze multiple data modalities for accurate diagnosis and staging.",
    icon: CpuChipIcon,
    colorClass: "text-blue-600",
    bgClass: "bg-blue-100",
  },
  {
    title: "Multimodal Data",
    description: "Analyze handwriting patterns, voice recordings, and medical reports for comprehensive health assessment.",
    icon: HeartIcon,
    colorClass: "text-green-600",
    bgClass: "bg-green-100",
  },
  {
    title: "Doctor Collaboration",
    description: "Secure platform for doctors to review AI analysis, verify results, and provide clinical oversight.",
    icon: UserGroupIcon,
    colorClass: "text-purple-600",
    bgClass: "bg-purple-100",
  },
  {
    title: "Progress Tracking",
    description: "Monitor health changes over time with detailed reports and trend analysis for better care management.",
    icon: ChartBarIcon,
    colorClass: "text-yellow-600",
    bgClass: "bg-yellow-100",
  },
  {
    title: "Lifestyle Recommendations",
    description: "Personalized lifestyle suggestions based on your stage and condition using an AI-powered system.",
    icon: BeakerIcon,
    colorClass: "text-red-600",
    bgClass: "bg-red-100",
  },
  {
    title: "HIPAA Compliant",
    description: "Secure, encrypted platform that protects your medical data with enterprise-grade security measures.",
    icon: ShieldCheckIcon,
    colorClass: "text-indigo-600",
    bgClass: "bg-indigo-100",
  },
];

const STEPS = [
  { step: "1", title: "Create Account", desc: "Sign up as a patient or healthcare provider to access the platform" },
  { step: "2", title: "Upload Data", desc: "Securely upload your medical data including handwriting samples, voice recordings, and doctor reports" },
  { step: "3", title: "AI Analysis", desc: "Our AI models analyze your data and generate comprehensive reports" },
  { step: "4", title: "Get Results", desc: "Receive detailed results and personalized care recommendations" },
];

// Memoized components for rendering performance (react-best-practices)
const FeatureCard = memo(({ feature, index }: { feature: typeof FEATURES[0], index: number }) => (
  <motion.div
    initial={{ opacity: 0, y: 40 }}
    whileInView={{ opacity: 1, y: 0 }}
    viewport={{ once: true, margin: "-50px" }}
    transition={{ duration: 0.5, delay: index * 0.1 }}
    className="text-center p-8 rounded-3xl bg-white border border-slate-100 shadow-sm hover:shadow-xl transition-all duration-300 cursor-pointer group"
  >
    <div className={`w-14 h-14 ${feature.bgClass} rounded-2xl flex items-center justify-center mx-auto mb-6 transform group-hover:scale-110 transition-transform duration-300`}>
      <feature.icon className={`h-7 w-7 ${feature.colorClass}`} aria-hidden="true" />
    </div>
    <h3 className="text-xl font-bold text-slate-900 mb-3">{feature.title}</h3>
    <p className="text-slate-600 leading-relaxed">{feature.description}</p>
  </motion.div>
));

const StepCard = memo(({ step, index }: { step: typeof STEPS[0], index: number }) => (
  <motion.div
    initial={{ opacity: 0, scale: 0.9 }}
    whileInView={{ opacity: 1, scale: 1 }}
    viewport={{ once: true, margin: "-50px" }}
    transition={{ duration: 0.5, delay: index * 0.15 }}
    className="text-center relative z-10"
  >
    <div className="w-20 h-20 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-full flex items-center justify-center mx-auto mb-6 text-white text-2xl font-bold shadow-lg shadow-blue-200 ring-8 ring-slate-50">
      {step.step}
    </div>
    <h3 className="text-xl font-bold text-slate-900 mb-3">{step.title}</h3>
    <p className="text-slate-600 leading-relaxed px-4">{step.desc}</p>
  </motion.div>
));

export default function LandingPage() {
  const { scrollYProgress } = useScroll();
  const yHeroText = useTransform(scrollYProgress, [0, 0.3], [0, 100]);
  const opacityHeroText = useTransform(scrollYProgress, [0, 0.3], [1, 0.2]);

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 selection:bg-blue-200 overflow-x-clip font-sans">
      {/* Navigation - Floating Navbar UI-UX-Pro-Max rule */}
      <nav className="fixed w-full z-50 bg-white/80 backdrop-blur-md border-b border-slate-200/50 transition-all duration-300">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-20">
            <GradientText
              colors={["#5227FF", "#33d17a", "#1a5fb4"]}
              animationSpeed={2.5}
              showBorder={false}
              className="text-2xl font-extrabold tracking-tight"
            >
              ParkinsonCare
            </GradientText>
            <div className="flex items-center space-x-6">
              <Link
                to="/login"
                className="text-slate-600 hover:text-blue-600 font-medium transition-colors"
                aria-label="Sign In to ParkinsonCare"
              >
                Sign In
              </Link>
              <Link
                to="/register"
                className="bg-slate-900 text-white hover:bg-slate-700 px-6 py-2.5 rounded-full font-medium transition-all shadow-sm cursor-pointer hover:shadow-md active:scale-95"
                aria-label="Get Started with ParkinsonCare"
              >
                Get Started
              </Link>
            </div>
          </div>
        </div>
      </nav>

      <main>
        {/* Dynamic Hero Section (Scroll Experience / Parallax Storytelling) */}
        <section className="relative pt-32 pb-20 lg:pt-48 lg:pb-32 overflow-hidden flex items-center justify-center min-h-[90vh]">
          {/* Background decorations */}
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-full overflow-hidden -z-10 pointer-events-none">
            <div className="absolute top-[-10%] left-[-10%] w-96 h-96 bg-blue-300/30 rounded-full blur-3xl opacity-60" />
            <div className="absolute bottom-[-10%] right-[-5%] w-96 h-96 bg-indigo-300/30 rounded-full blur-3xl opacity-60" />
          </div>

          <div className="relative w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center z-10 flex flex-col items-center justify-center min-h-[400px]">
            <div style={{ width: '100%', height: '400px', position: 'absolute', inset: 0, zIndex: -1 }}>
              <Antigravity
                count={300}
                magnetRadius={22}
                ringRadius={14}
                waveSpeed={0.4}
                waveAmplitude={1}
                particleSize={1.7}
                lerpSpeed={0.05}
                color="#9141ac"
                autoAnimate
                particleVariance={1}
                rotationSpeed={0}
                depthFactor={1}
                pulseSpeed={3}
                particleShape="capsule"
                fieldStrength={10}
              />
            </div>

            <motion.div style={{ y: yHeroText, opacity: opacityHeroText }}>
              <motion.h1
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, ease: "easeOut" }}
                className="text-5xl md:text-7xl font-extrabold tracking-tight text-slate-900 mb-8 mt-12 pointer-events-none"
              >
                AI-Powered <br className="hidden md:block" />
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">
                  Parkinson's Detection
                </span>
              </motion.h1>
              <motion.p
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: 0.2, ease: "easeOut" }}
                className="text-xl md:text-2xl text-slate-600 mb-10 max-w-3xl mx-auto leading-relaxed"
              >
                A proactive, diagnostic platform combining handwriting analysis,
                voice assessment, and medical intelligence for earlier intervention.
              </motion.p>
              <motion.div
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: 0.4, ease: "easeOut" }}
                className="flex flex-col sm:flex-row items-center justify-center gap-4"
              >
                <Link
                  to="/analysis"
                  className="w-full sm:w-auto bg-blue-600 text-white hover:bg-blue-700 px-8 py-4 rounded-full text-lg font-bold transition-all transform hover:scale-[1.02] shadow-xl shadow-blue-600/20 cursor-pointer active:scale-[0.98]"
                >
                  Start AI Analysis
                </Link>
                <Link
                  to="/about"
                  className="w-full sm:w-auto bg-white text-slate-800 border border-slate-200 hover:bg-slate-50 hover:border-slate-300 px-8 py-4 rounded-full text-lg font-bold transition-all cursor-pointer shadow-sm active:scale-[0.98]"
                >
                  Learn More
                </Link>
              </motion.div>
            </motion.div>
          </div>
        </section>

        {/* Features Section */}
        <section className="py-32 bg-white relative">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <motion.div
              initial={{ opacity: 0, y: 40 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-100px" }}
              transition={{ duration: 0.6 }}
              className="text-center mb-20"
            >
              <h2 className="text-4xl md:text-5xl font-extrabold text-slate-900 mb-6 tracking-tight">
                Comprehensive Health Tracking
              </h2>
              <p className="text-xl text-slate-600 max-w-2xl mx-auto">
                Our platform aggregates multiple non-invasive data markers to accurately track
                disease progression securely over time.
              </p>
            </motion.div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 xgap-10">
              {FEATURES.map((feature, idx) => (
                <FeatureCard key={feature.title} feature={feature} index={idx} />
              ))}
            </div>
          </div>
        </section>

        {/* How It Works Section */}
        <section className="py-32 bg-slate-50 relative overflow-hidden">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <motion.div
              initial={{ opacity: 0, y: 40 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-100px" }}
              transition={{ duration: 0.6 }}
              className="text-center mb-24"
            >
              <h2 className="text-4xl md:text-5xl font-extrabold text-slate-900 mb-6 tracking-tight">
                How It Works
              </h2>
              <p className="text-xl text-slate-600 max-w-2xl mx-auto">
                A simple, intelligent assessment pipeline built for seamless accessibility.
              </p>
            </motion.div>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-12 relative">
              {/* Connector Line for Desktop */}
              <div className="hidden md:block absolute top-[2.5rem] left-[12.5%] right-[12.5%] h-[2px] bg-slate-200 z-0" />

              {STEPS.map((step, idx) => (
                <StepCard key={step.step} step={step} index={idx} />
              ))}
            </div>
          </div>
        </section>

        {/* Cinematic CTA Section with Parallax Overlay */}
        <section className="relative py-40 overflow-hidden bg-slate-900 border-t border-slate-800">
          <motion.div
            className="absolute inset-0 z-0 opacity-40 mix-blend-overlay"
            style={{ y: useTransform(scrollYProgress, [0.7, 1], [-150, 150]) }}
          >
            <div className="absolute w-full h-full bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-indigo-500/20 via-slate-900/10 to-slate-900" />
          </motion.div>

          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center relative z-10">
            <motion.h2
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              whileInView={{ opacity: 1, scale: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.7 }}
              className="text-5xl md:text-6xl font-extrabold text-white mb-8 tracking-tight"
            >
              Take control of your timeline.
            </motion.h2>
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.7, delay: 0.2 }}
              className="text-xl text-slate-300 mb-12 max-w-2xl mx-auto"
            >
              Join patients and healthcare providers utilizing our machine learning
              engine for rigorous tracking and personalized medical interventions.
            </motion.p>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.7, delay: 0.3 }}
            >
              <Link
                to="/analysis"
                className="inline-block bg-white text-slate-900 hover:bg-slate-100 font-bold py-4 px-10 rounded-full text-lg transition duration-200 transform hover:scale-[1.03] shadow-2xl shadow-white/5 cursor-pointer active:scale-[0.98]"
              >
                Launch Dashboard
              </Link>
            </motion.div>
          </div>
        </section>
      </main>

      {/* Modern High-Contrast Footer */}
      <footer className="bg-slate-950 text-slate-400 py-16 border-t border-slate-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-12 mb-12">
            <div className="col-span-1 md:col-span-1">
              <h3 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-indigo-400 mb-4">
                ParkinsonCare
              </h3>
              <p className="text-sm leading-relaxed text-slate-500">
                Pioneering AI-powered platform for the early detection, tracking, and
                personalized care of Parkinson's disease.
              </p>
            </div>

            <div>
              <h4 className="text-sm font-bold text-slate-300 uppercase tracking-wider mb-6">Platform</h4>
              <ul className="space-y-4 text-sm">
                <li><Link to="/features" className="hover:text-blue-400 transition-colors">Features</Link></li>
                <li><Link to="/pricing" className="hover:text-blue-400 transition-colors">Pricing</Link></li>
                <li><Link to="/security" className="hover:text-blue-400 transition-colors">Security</Link></li>
              </ul>
            </div>

            <div>
              <h4 className="text-sm font-bold text-slate-300 uppercase tracking-wider mb-6">Support</h4>
              <ul className="space-y-4 text-sm">
                <li><Link to="/help" className="hover:text-blue-400 transition-colors">Help Center</Link></li>
                <li><Link to="/contact" className="hover:text-blue-400 transition-colors">Contact Us</Link></li>
                <li><Link to="/docs" className="hover:text-blue-400 transition-colors">Documentation</Link></li>
              </ul>
            </div>

            <div>
              <h4 className="text-sm font-bold text-slate-300 uppercase tracking-wider mb-6">Legal</h4>
              <ul className="space-y-4 text-sm">
                <li><Link to="/privacy" className="hover:text-blue-400 transition-colors">Privacy Policy</Link></li>
                <li><Link to="/terms" className="hover:text-blue-400 transition-colors">Terms of Service</Link></li>
                <li><Link to="/hipaa" className="hover:text-blue-400 transition-colors">HIPAA Compliance</Link></li>
              </ul>
            </div>
          </div>

          <div className="border-t border-slate-800/60 pt-8 flex flex-col md:flex-row justify-between items-center text-sm">
            <p>&copy; {new Date().getFullYear()} ParkinsonCare. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
