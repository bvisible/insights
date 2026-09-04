<template>
	<div class="flex h-screen w-screen overflow-hidden bg-white text-base antialiased">
		<!-- //// Neoffice — upstream renders its own <AppSidebar> here (in a wrapper
		     //// carrying border-r bg-gray-50). We mount NeoCockpitInsightsSidebar
		     //// instead: the shared Neoffice chrome (module switcher, NORA, mail,
		     //// notifications) must be the same on every surface — ADR-015. The
		     //// wrapper classes go too, the cockpit paints its own frame. The native
		     //// AppSidebar is not lost: the sidebar falls back to it when the
		     //// cockpit bundle cannot load. -->
		<div v-if="!hideSidebar" class="h-full">
			<NeoCockpitInsightsSidebar />
		</div>

		<div class="flex h-full flex-1 flex-col overflow-auto">
			<Suspense>
				<RouterView />
			</Suspense>
		</div>

		<template>
			<component v-for="dialog in dialogs" :is="dialog" :key="dialog.id" />
		</template>

		<Toaster
			position="bottom-right"
			:expand="true"
			:close-button="true"
			:toast-options="{ duration: 4000 }"
		/>
	</div>
</template>

<script setup lang="ts">
import { computed, ref, watchEffect } from 'vue'
import { useRoute } from 'vue-router'
import { Toaster } from 'vue-sonner'
//// Neoffice — replaces `import AppSidebar from './components/AppSidebar.vue'`
//// (see the template above). AppSidebar.vue itself is untouched and still
//// imported by NeoCockpitInsightsSidebar as the fallback.
import NeoCockpitInsightsSidebar from './components/NeoCockpitInsightsSidebar.vue'
import { dialogs } from './helpers/confirm_dialog'
import { attachRealtimeListener, waitUntil } from './helpers/index.ts'
import { createToast } from './helpers/toasts.ts'
import session from './session'
import telemetry from './telemetry.ts'
import router from '@/router.ts'

const route = useRoute()
const hideSidebar = ref(true)
watchEffect(() => {
	if (route.fullPath === '/') return
	hideSidebar.value = Boolean(route.meta.isGuestView || route.meta.hideSidebar)
})

const isGuestView = computed(() => route.meta.isGuestView || !session.isLoggedIn)
waitUntil(() => session.isLoggedIn).then(() => {
	telemetry.init()
})

attachRealtimeListener('insights_notification', (data: any) => {
	if (data.user == session.user.email) {
		createToast({
			title: data.title || data.message,
			message: data.title ? data.message : '',
			variant: data.type,
			duration: data.duration ? data.duration * 1000 : 4000,
		})
	}
})
</script>
