// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

// https://astro.build/config
export default defineConfig({
	site: 'https://Hrushi11.github.io',
	base: '/AgentSpine',
	integrations: [
		starlight({
			title: 'AgentSpine Docs',
			favicon: '/favicon.png',
			logo: {
				src: './src/assets/logo.png',
			},
			social: [
				{ icon: 'github', label: 'GitHub', href: 'https://github.com/Hrushi11/AgentSpine' }
			],
			sidebar: [
				{
					label: 'Introduction',
					link: '/',
				},
				{
					label: 'Guides',
					items: [
						{ label: 'Getting Started', slug: 'getting-started' },
						{ label: 'Configuration', slug: 'configuration' },
					],
				},
				{
					label: 'Architecture',
					items: [
						{ label: 'Core Concepts', slug: 'concepts' },
						{ label: 'Pipeline Model', slug: 'pipeline' },
						{ label: 'Deployment', slug: 'deployment' },
						{ label: 'Plugins', slug: 'plugins' },
					],
				},
				{
					label: 'Reference',
					items: [
						{ label: 'API Reference', slug: 'api' },
					],
				},
			],
			customCss: [
				'./src/styles/custom.css',
			],
		}),
	],
});
