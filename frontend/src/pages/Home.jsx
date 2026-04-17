import { Navbar } from "../components/Navbar";
import { Hero } from "../components/Hero";
import { Features } from "../components/Features";
import { HowItWorks } from "../components/HowItWorks";
import { FinalCTA } from "../components/FinalCTA";
import { Footer } from "../components/Footer";

const Home = () => {
  return (
    <div className="min-h-screen bg-white selection:bg-primary selection:text-white">
      <Navbar />
      <main>
        <Hero />
        <Features />
        <HowItWorks />
        <FinalCTA />
      </main>
      <Footer />
    </div>
  );
};

export default Home;
