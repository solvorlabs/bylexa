import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { FaProjectDiagram, FaPlusCircle, FaShieldAlt, FaRobot } from 'react-icons/fa';

const features = [
  {
    title: 'Project Vault',
    description: 'Track every automation initiative from one polished workspace.',
    icon: FaProjectDiagram,
    link: '/project-list',
  },
  {
    title: 'Create Mission',
    description: 'Spin up a new project with a focused setup flow.',
    icon: FaPlusCircle,
    link: '/create',
  },
  {
    title: 'Command Center',
    description: 'Run voice-driven and secure OS workflows from a single console.',
    icon: FaShieldAlt,
    link: '/os-command',
  },
  {
    title: 'AI Co-Pilot',
    description: 'Collaborate with Bylexa assistant for planning and execution.',
    icon: FaRobot,
    link: '/assistant',
  },
];

const Features = () => {
  return (
    <section className="relative z-20 bg-neutral-950 px-6 pb-24 pt-10 text-white md:px-10">
      <div className="mx-auto max-w-7xl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.3 }}
          transition={{ duration: 0.6 }}
          className="mb-12"
        >
          <p className="mb-3 text-xs uppercase tracking-[0.28em] text-cyan-200/80">Core Experiences</p>
          <h2 className="font-display text-4xl leading-tight sm:text-5xl">Fewer pages. Higher signal.</h2>
          <p className="mt-4 max-w-2xl text-slate-300">
            The interface now emphasizes the essential Bylexa journeys with a consistent premium visual language.
          </p>
        </motion.div>

        <div className="grid gap-6 md:grid-cols-2">
        {features.map((feature, index) => (
          <motion.div
            key={feature.title}
            initial={{ opacity: 0, y: 24 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, amount: 0.3 }}
            transition={{ duration: 0.5, delay: index * 0.06 }}
          >
            <Link
              to={feature.link}
              className="group relative flex h-full min-h-52 flex-col justify-between overflow-hidden rounded-2xl border border-white/10 bg-gradient-to-b from-slate-900/70 to-black p-6 transition duration-300 hover:border-cyan-300/40 hover:shadow-[0_0_35px_rgba(34,211,238,0.18)]"
            >
              <div className="absolute inset-0 bg-[radial-gradient(circle_at_100%_0%,rgba(34,211,238,0.2),transparent_40%)] opacity-0 transition-opacity duration-300 group-hover:opacity-100" />
              <feature.icon className="relative z-10 mb-7 text-4xl text-cyan-300" />
              <div className="relative z-10">
                <h3 className="mb-2 text-2xl font-semibold text-white">{feature.title}</h3>
                <p className="text-sm leading-relaxed text-slate-300">{feature.description}</p>
              </div>
            </Link>
          </motion.div>
        ))}
        </div>
      </div>
    </section>
  );
};

export default Features;
