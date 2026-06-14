import { frappeRequest, setConfig } from 'frappe-ui'
import { GridItem, GridLayout } from 'grid-layout-plus'
import { createPinia } from 'pinia'
import { createApp } from 'vue'
import App from './App.vue'
import { registerControllers, registerGlobalComponents } from './globals.ts'
import './index.css'
import router from './router.ts'
import { translationPlugin } from './translation.ts'
import { spritePlugin } from 'frappe-ui/icons'

// Adopt the shared cockpit colour mode (neocockpit-colormode) on startup so the
// Insights SPA + its charts follow the product theme even when the NeoCockpit
// chrome doesn't propagate data-theme to this document. //// neoffice
;(function applyNeoColorMode() {
	const apply = () => {
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
