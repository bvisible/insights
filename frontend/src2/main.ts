import { frappeRequest, setConfig } from 'frappe-ui'
import { spritePlugin } from 'frappe-ui/icons'
import { GridItem, GridLayout } from 'grid-layout-plus'
import { createPinia } from 'pinia'
import { createApp, watchEffect } from 'vue'
import App from './App.vue'
import { registerControllers, registerGlobalComponents } from './globals.ts'
import './index.css'
import router from './router.ts'
import { translationPlugin } from './translation.ts'
import telemetryPlugin from './telemetry'
import session from './session.ts'

// Adopt the shared cockpit colour mode (neocockpit-colormode) on startup so the
// Insights SPA + its charts follow the product theme even when the NeoCockpit
// chrome doesn't propagate data-theme to this document. //// neoffice
;(function applyNeoColorMode() {
	const apply = () => {
		//// neoffice — once the cockpit has set the theme it decides (it writes data-theme-mode, from the reader's
		//// desk theme): a system change must not turn the page back to the guess below under a cockpit that stays
		//// light (07.10).
		if (document.documentElement.hasAttribute('data-theme-mode')) return
		let mode = 'system'
		try {
			mode = localStorage.getItem('neocockpit-colormode') || 'system'
		} catch (e) {
			/* noop */
		}
		const sysDark =
			typeof matchMedia !== 'undefined' && matchMedia('(prefers-color-scheme: dark)').matches
		const theme = mode === 'system' ? (sysDark ? 'dark' : 'light') : mode
		document.documentElement.setAttribute('data-theme', theme)
		document.documentElement.classList.toggle('dark', theme === 'dark')
	}
	apply()
	try {
		matchMedia('(prefers-color-scheme: dark)').addEventListener('change', apply)
	} catch (e) {
		/* noop */
	}
	//// neoffice — the `dark` class Insights' components read follows data-theme, whoever sets it. The cockpit sets
	//// data-theme from the reader's desk theme once it mounts, after the guess above; the class stayed on the guess.
	//// With the computer in dark mode and the desk theme Light, the page turned dark under a light cockpit, its
	//// labels dark on dark (07.10).
	try {
		new MutationObserver(() => {
			const html = document.documentElement
			const dark = html.getAttribute('data-theme') === 'dark'
			if (html.classList.contains('dark') !== dark) html.classList.toggle('dark', dark)
		}).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] })
	} catch (e) {
		/* noop */
	}
	window.addEventListener('storage', (e) => {
		if (e.key === 'neocockpit-colormode') apply()
	})
})()

setConfig('resourceFetcher', frappeRequest)

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.use(spritePlugin)
app.component('grid-layout', GridLayout)
app.component('grid-item', GridItem)

const stop = watchEffect(() => {
	if (session.isLoggedIn) {
		app.use(telemetryPlugin, { app_name: 'insights' })
		stop()
	}
})

app.config.errorHandler = (err, vm, info) => {
	console.groupCollapsed('Unhandled Error in: ', info)
	console.error('Context:', vm)
	console.error('Error:', err)
	console.groupEnd()
	return false
}

registerGlobalComponents(app)
registerControllers(app)

app.mount('#app')
app.use(translationPlugin);
