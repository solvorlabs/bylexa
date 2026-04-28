import React from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';

const Hero = () => {
    return (
        <section className="relative isolate min-h-screen overflow-hidden bg-neutral-950 text-white">
            <video autoPlay loop muted playsInline className="absolute inset-0 w-full h-full object-cover z-0">
                <source src="https://res.cloudinary.com/dfonotyfb/video/upload/v1775585556/dds3_1_rqhg7x.mp4" type="video/mp4" />
            </video>

            <div className="absolute inset-0 z-10 bg-gradient-to-b from-black/70 via-black/55 to-black/90" />
            <div className="absolute inset-0 z-10 bg-[radial-gradient(circle_at_20%_20%,rgba(14,165,233,0.2),transparent_48%),radial-gradient(circle_at_80%_75%,rgba(125,211,252,0.15),transparent_45%)]" />

            <div className="relative z-20 mx-auto flex min-h-screen max-w-7xl items-center px-6 pt-24 pb-20 md:px-10">
                <motion.div
                    initial={{ opacity: 0, y: 24 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.9, ease: 'easeOut' }}
                    className="max-w-3xl"
                >
                    <p className="mb-4 inline-flex items-center gap-2 rounded-full border border-cyan-300/35 bg-black/30 px-4 py-2 text-xs uppercase tracking-[0.32em] text-cyan-100/90 backdrop-blur-sm">
                        Intelligent Automation Platform
                    </p>

                    <h1 className="font-display text-5xl leading-tight text-white sm:text-6xl md:text-7xl lg:text-8xl">
                        Bylexa
                    </h1>

                    <p className="mt-6 max-w-2xl text-base leading-relaxed text-slate-200 sm:text-lg">
                        Command projects, scripts, and system actions from one cinematic control surface.
                        Built for precision workflows powered by voice and AI.
                    </p>

                    <div className="mt-10 flex flex-col gap-4 sm:flex-row">
                        <Link
                            to="/os-command"
                            className="inline-flex items-center justify-center rounded-full border border-cyan-300/60 bg-cyan-400/10 px-7 py-3 text-sm font-semibold uppercase tracking-[0.2em] text-cyan-100 transition hover:bg-cyan-300/20"
                        >
                            Launch Command
                        </Link>
                        <Link
                            to="/project-list"
                            className="inline-flex items-center justify-center rounded-full border border-white/25 bg-black/35 px-7 py-3 text-sm font-semibold uppercase tracking-[0.2em] text-slate-100 transition hover:border-white/45 hover:bg-black/55"
                        >
                            Explore Projects
                        </Link>
                    </div>
                </motion.div>
            </div>
        </section>
    );
};

export default Hero;
