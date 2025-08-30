import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { Button } from "../components/ui/button";
import { Card } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import {
  ArrowRight,
  Shield,
  Globe,
  Clock,
  UserCheck,
  FileText,
  Zap,
  CheckCircle,
  MessageSquare,
  Users,
  AlertTriangle,
  Award,
  BarChart3,
  Stethoscope,
  Languages,
  ShieldCheck,
  Activity,
  Sparkles,
  Calendar,
  Upload,
  Edit3,
} from "lucide-react";

const fadeInUp = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.5 }
};

const staggerContainer = {
  animate: {
    transition: {
      staggerChildren: 0.1
    }
  }
};

export function LandingPage() {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 pb-20 pt-32">
        <div className="absolute inset-0 bg-grid-slate-100 [mask-image:linear-gradient(0deg,white,rgba(255,255,255,0.6))] bg-fixed"></div>
        
        {/* Animated background shapes */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-40 -right-40 h-80 w-80 rounded-full bg-gradient-to-br from-blue-200 to-purple-200 opacity-20 blur-3xl animate-pulse"></div>
          <div className="absolute -bottom-40 -left-40 h-80 w-80 rounded-full bg-gradient-to-br from-green-200 to-blue-200 opacity-20 blur-3xl animate-pulse delay-1000"></div>
        </div>

        <div className="container relative mx-auto px-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="mx-auto max-w-5xl text-center"
          >
            <Badge className="mb-4 bg-blue-100 text-blue-700 border-blue-200 px-4 py-1">
              <Sparkles className="w-3 h-3 mr-1" />
              AI-Powered Healthcare for India
            </Badge>
            
            <h1 className="mb-6 text-5xl font-bold tracking-tight text-gray-900 sm:text-6xl lg:text-7xl">
              Cut your paperwork in{" "}
              <span className="bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                half
              </span>
              <br />
              Let AI handle intake
            </h1>
            
            <p className="mb-10 text-xl text-gray-600 sm:text-2xl max-w-3xl mx-auto">
              Multilingual AI intake with safety guardrails. English summaries for doctors. 
              Built for India's healthcare needs.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-8">
              <Button size="lg" className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white px-8 py-6 text-lg rounded-full shadow-xl hover:shadow-2xl transition-all transform hover:-translate-y-1">
                Book a Demo
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
              <Button size="lg" variant="outline" className="px-8 py-6 text-lg rounded-full border-2 hover:bg-white/50 backdrop-blur">
                See Sample Intake
                <MessageSquare className="ml-2 h-5 w-5" />
              </Button>
            </div>

            <div className="flex flex-wrap justify-center gap-6 text-sm text-gray-600">
              <div className="flex items-center gap-1">
                <CheckCircle className="h-4 w-4 text-green-600" />
                <span>DPDPA 2023 Aligned</span>
              </div>
              <div className="flex items-center gap-1">
                <Shield className="h-4 w-4 text-green-600" />
                <span>AWS India Hosted</span>
              </div>
              <div className="flex items-center gap-1">
                <Globe className="h-4 w-4 text-green-600" />
                <span>Multilingual Support</span>
              </div>
              <div className="flex items-center gap-1">
                <ShieldCheck className="h-4 w-4 text-green-600" />
                <span>Enterprise Security</span>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-white">
        <div className="container mx-auto px-4">
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            className="text-center mb-12"
          >
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Built for India's Healthcare
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Every feature designed with Indian clinics, doctors, and patients in mind
            </p>
          </motion.div>

          <motion.div
            variants={staggerContainer}
            initial="initial"
            whileInView="animate"
            viewport={{ once: true }}
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
          >
            {[
              {
                icon: Languages,
                title: "Multilingual Intake",
                description: "Patients speak in Hindi, Tamil, Telugu, or any language. Doctors get clean English summaries.",
                color: "blue"
              },
              {
                icon: AlertTriangle,
                title: "Red Flag Detection",
                description: "Auto-escalation for compartment syndrome, cauda equina, septic arthritis, and more.",
                color: "red"
              },
              {
                icon: Stethoscope,
                title: "Ortho-Ready",
                description: "Specialized question banks for orthopedics with MOI, weight-bearing status, and ROM capture.",
                color: "green"
              },
              {
                icon: ShieldCheck,
                title: "Never Diagnoses",
                description: "100% safety guardrails. AI gathers info only. RMP reviews and advises. Full compliance.",
                color: "purple"
              },
              {
                icon: Zap,
                title: "Lightning Fast",
                description: "P95 ≤1.5s text response, ≤3.0s voice. Handles 200+ concurrent sessions effortlessly.",
                color: "yellow"
              },
              {
                icon: FileText,
                title: "Lightweight EMR",
                description: "One-click SOAP notes, e-signatures, version history, and FHIR-lite export ready.",
                color: "indigo"
              }
            ].map((feature, index) => (
              <motion.div key={index} variants={fadeInUp}>
                <Card className="p-6 h-full hover:shadow-xl transition-shadow duration-300 border-gray-100 group hover:border-blue-200">
                  <div className={`inline-flex p-3 rounded-lg bg-${feature.color}-50 group-hover:bg-${feature.color}-100 transition-colors mb-4`}>
                    <feature.icon className={`h-6 w-6 text-${feature.color}-600`} />
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">
                    {feature.title}
                  </h3>
                  <p className="text-gray-600">
                    {feature.description}
                  </p>
                </Card>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-20 bg-gradient-to-b from-gray-50 to-white">
        <div className="container mx-auto px-4">
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            className="text-center mb-12"
          >
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Simple 3-Step Process
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              From booking to completed notes in minutes
            </p>
          </motion.div>

          <div className="max-w-4xl mx-auto">
            <motion.div
              initial="initial"
              whileInView="animate"
              viewport={{ once: true }}
              variants={staggerContainer}
              className="space-y-8"
            >
              {[
                {
                  step: "1",
                  title: "Book & Verify",
                  description: "Patients pick a slot (physical or Zoom). Receive secure magic link/OTP to start intake.",
                  icon: Calendar,
                  color: "blue"
                },
                {
                  step: "2",
                  title: "AI-Powered Intake",
                  description: "Speak naturally in any Indian language. AI extracts HPI, PMH, medications, allergies, and detects red flags.",
                  icon: MessageSquare,
                  color: "green"
                },
                {
                  step: "3",
                  title: "Doctor Review & Sign",
                  description: "Single-pane English summary with safety chips. Accept to SOAP, edit inline, and e-sign.",
                  icon: Edit3,
                  color: "purple"
                }
              ].map((step, index) => (
                <motion.div
                  key={index}
                  variants={fadeInUp}
                  className="flex gap-6 items-start"
                >
                  <div className={`flex-shrink-0 w-16 h-16 rounded-full bg-${step.color}-100 flex items-center justify-center border-2 border-${step.color}-200`}>
                    <span className={`text-2xl font-bold text-${step.color}-700`}>
                      {step.step}
                    </span>
                  </div>
                  <div className="flex-grow">
                    <div className="bg-white rounded-xl p-6 shadow-md hover:shadow-lg transition-shadow">
                      <div className="flex items-center gap-3 mb-3">
                        <step.icon className={`h-6 w-6 text-${step.color}-600`} />
                        <h3 className="text-xl font-semibold text-gray-900">
                          {step.title}
                        </h3>
                      </div>
                      <p className="text-gray-600">
                        {step.description}
                      </p>
                    </div>
                  </div>
                </motion.div>
              ))}
            </motion.div>
          </div>
        </div>
      </section>

      {/* Trust & Security Section */}
      <section className="py-20 bg-white">
        <div className="container mx-auto px-4">
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            className="text-center mb-12"
          >
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Enterprise-Grade Security
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Built with India's data protection laws in mind
            </p>
          </motion.div>

          <div className="max-w-4xl mx-auto">
            <motion.div
              initial="initial"
              whileInView="animate"
              viewport={{ once: true }}
              variants={staggerContainer}
              className="grid grid-cols-1 md:grid-cols-3 gap-6"
            >
              {[
                { label: "DPDPA 2023", sublabel: "Compliant" },
                { label: "Telemedicine 2020", sublabel: "Aligned" },
                { label: "AWS India", sublabel: "ap-south-1/2" }
              ].map((item, index) => (
                <motion.div key={index} variants={fadeInUp}>
                  <Card className="p-8 text-center bg-gradient-to-br from-gray-50 to-white border-gray-100 h-full">
                    <Shield className="h-12 w-12 text-green-600 mx-auto mb-4" />
                    <div className="text-xl font-bold text-gray-900 mb-1">{item.label}</div>
                    <div className="text-sm text-gray-600">{item.sublabel}</div>
                  </Card>
                </motion.div>
              ))}
            </motion.div>

            <motion.div
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
              transition={{ delay: 0.3 }}
              className="mt-12 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-2xl p-8"
            >
              <div className="flex flex-col lg:flex-row items-center justify-between gap-6">
                <div>
                  <h3 className="text-2xl font-bold text-gray-900 mb-2">
                    Safety First Architecture
                  </h3>
                  <ul className="space-y-2 text-gray-600">
                    <li className="flex items-center gap-2">
                      <CheckCircle className="h-5 w-5 text-green-600" />
                      AES-256 encryption at rest, TLS 1.3 in transit
                    </li>
                    <li className="flex items-center gap-2">
                      <CheckCircle className="h-5 w-5 text-green-600" />
                      Immutable audit logs for all PHI access
                    </li>
                    <li className="flex items-center gap-2">
                      <CheckCircle className="h-5 w-5 text-green-600" />
                      AI never provides diagnosis to patients
                    </li>
                  </ul>
                </div>
                <Button variant="outline" size="lg" className="whitespace-nowrap">
                  Download Security Brief
                  <FileText className="ml-2 h-5 w-5" />
                </Button>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="py-20 bg-gray-50">
        <div className="container mx-auto px-4">
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            className="text-center mb-12"
          >
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Trusted by Leading Clinics
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              See what doctors are saying about Baymax
            </p>
          </motion.div>

          <motion.div
            initial="initial"
            whileInView="animate"
            viewport={{ once: true }}
            variants={staggerContainer}
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-5xl mx-auto"
          >
            {[
              {
                quote: "Our ortho OPD runs noticeably faster. The red-flag chips are clutch.",
                author: "Dr. Rajesh Kumar",
                role: "Senior RMP, Mumbai",
                avatar: "👨‍⚕️"
              },
              {
                quote: "Patients finish intake in their language; I read in English and sign in minutes.",
                author: "Dr. Priya Sharma",
                role: "Orthopedic Surgeon, Bengaluru",
                avatar: "👩‍⚕️"
              },
              {
                quote: "Finally, an EMR that doesn't slow us down. The AI intake is a game-changer.",
                author: "Dr. Amit Patel",
                role: "Clinic Director, Delhi",
                avatar: "👨‍⚕️"
              }
            ].map((testimonial, index) => (
              <motion.div key={index} variants={fadeInUp}>
                <Card className="p-6 h-full bg-white">
                  <div className="flex items-center gap-3 mb-4">
                    <div className="text-3xl">{testimonial.avatar}</div>
                    <div>
                      <div className="font-semibold text-gray-900">{testimonial.author}</div>
                      <div className="text-sm text-gray-600">{testimonial.role}</div>
                    </div>
                  </div>
                  <p className="text-gray-700 italic">"{testimonial.quote}"</p>
                  <div className="flex gap-1 mt-4">
                    {[...Array(5)].map((_, i) => (
                      <span key={i} className="text-yellow-500">★</span>
                    ))}
                  </div>
                </Card>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-blue-600 to-indigo-600 text-white">
        <div className="container mx-auto px-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            className="text-center max-w-3xl mx-auto"
          >
            <h2 className="text-4xl font-bold mb-4">
              Ready to Transform Your Practice?
            </h2>
            <p className="text-xl mb-8 text-blue-100">
              Join leading clinics across India using AI to reduce paperwork and improve patient care
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button size="lg" className="bg-white text-blue-600 hover:bg-gray-100 px-8 py-6 text-lg rounded-full">
                Start Your Pilot
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
              <Button size="lg" variant="outline" className="border-2 border-white text-white bg-white/10 hover:bg-white/20 px-8 py-6 text-lg rounded-full">
                Schedule Demo
                <Calendar className="ml-2 h-5 w-5" />
              </Button>
            </div>
            <p className="mt-6 text-sm text-blue-100">
              No credit card required • 30-day pilot • Full support included
            </p>
          </motion.div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="py-20 bg-white">
        <div className="container mx-auto px-4">
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            className="text-center mb-12"
          >
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Frequently Asked Questions
            </h2>
          </motion.div>

          <motion.div
            initial="initial"
            whileInView="animate"
            viewport={{ once: true }}
            variants={staggerContainer}
            className="max-w-3xl mx-auto space-y-6"
          >
            {[
              {
                q: "Does the AI give patients a diagnosis?",
                a: "No. The AI only gathers information. An RMP reviews and advises. The system enforces guardrails to block diagnosis/medication advice to patients."
              },
              {
                q: "Is it compliant with India regulations?",
                a: "Yes—aligned with DPDPA 2023 and Telemedicine Guidelines 2020. PHI is hosted in AWS India and encrypted in transit and at rest."
              },
              {
                q: "What languages are supported?",
                a: "Patients can speak/type in multiple Indian languages and even code-switch. Doctors receive English summaries."
              },
              {
                q: "What happens if a red flag appears?",
                a: "Patients see emergency guidance, the assigned doctor is paged immediately, and the event is logged."
              }
            ].map((faq, index) => (
              <motion.div key={index} variants={fadeInUp}>
                <Card className="p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    {faq.q}
                  </h3>
                  <p className="text-gray-600">
                    {faq.a}
                  </p>
                </Card>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Enhanced Footer */}
      <footer className="bg-gray-900 text-gray-300 py-12">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <span className="text-2xl">🩺</span>
                <span className="text-xl font-bold text-white">Baymax</span>
              </div>
              <p className="text-sm">
                AI-powered patient intake for India's healthcare
              </p>
            </div>
            
            <div>
              <h4 className="font-semibold text-white mb-3">Product</h4>
              <ul className="space-y-2 text-sm">
                <li><Link to="#" className="hover:text-white">Features</Link></li>
                <li><Link to="#" className="hover:text-white">How it Works</Link></li>
                <li><Link to="#" className="hover:text-white">Pricing</Link></li>
                <li><Link to="#" className="hover:text-white">Demo</Link></li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-semibold text-white mb-3">Resources</h4>
              <ul className="space-y-2 text-sm">
                <li><Link to="#" className="hover:text-white">Documentation</Link></li>
                <li><Link to="#" className="hover:text-white">API Reference</Link></li>
                <li><Link to="#" className="hover:text-white">Security</Link></li>
                <li><Link to="#" className="hover:text-white">Compliance</Link></li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-semibold text-white mb-3">Company</h4>
              <ul className="space-y-2 text-sm">
                <li><Link to="#" className="hover:text-white">About</Link></li>
                <li><Link to="#" className="hover:text-white">Contact</Link></li>
                <li><Link to="#" className="hover:text-white">Privacy</Link></li>
                <li><Link to="#" className="hover:text-white">Terms</Link></li>
              </ul>
            </div>
          </div>
          
          <div className="border-t border-gray-800 pt-8 flex flex-col md:flex-row justify-between items-center gap-4">
            <p className="text-sm">
              © {new Date().getFullYear()} Baymax. All rights reserved.
            </p>
            <p className="text-xs text-gray-400 text-center">
              Baymax supports RMP-led telemedicine. It does not provide medical diagnosis or prescribe medications. For emergencies, call 112.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default LandingPage;