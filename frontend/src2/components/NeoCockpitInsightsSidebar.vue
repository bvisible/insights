<template>
	<AppSidebar v-if="failed" />
	<NeoCockpitBridge
		v-else
		:surface-app="surfaceApp"
		:context-nav="contextNav"
		:navigate="navigate"
		@failed="failed = true"
	/>
</template>

<script setup lang="ts">
/**
 * Insights flavor of the shared Neoffice chrome (NeoCockpit). Maps the
 * fixed links into contextNav; native AppSidebar kept as auto fallback.
 * Recipe: neoffice ADR-015.
 */
import AppSidebar from './AppSidebar.vue'
import NeoCockpitBridge from './NeoCockpitBridge.vue'

import { useRouter, useRoute } from 'vue-router'
import { ref, computed } from 'vue'
import settingsStore from '../settings/settings'

const router = useRouter()
const route = useRoute()
const failed = ref(false)
const settings = settingsStore()

const surfaceApp = {
	name: 'insights',
	title: 'Insights',
	logo: '/assets/insights/frontend/insights-logo-new.svg',
}

function navigate(r: string) {
	if (!r) return
	if (r.startsWith('/app') || r.startsWith('http')) window.location.href = r
	else router.push(r)
}

const contextNav = computed(() => {
	const currentName = String(route.name || '')
	const items = [
		{ label: __('Dashboards'), icon: 'lucide-layout-grid', to: 'DashboardList' },
		{ label: __('Workbooks'), icon: 'lucide-book', to: 'WorkbookList' },
		{ label: __('Data Sources'), icon: 'lucide-database', to: 'DataSourceList' },
	]
	if (settings.doc?.enable_data_store) {
		items.push({ label: __('Data Store'), icon: 'lucide-database-zap', to: 'DataStoreList' })
	}
	return [
		{
			items: items.map((item) => ({
				label: item.label,
				icon: item.icon,
				active: currentName === item.to || currentName.startsWith(item.to.replace('List', '')),
				onClick: () => router.push({ name: item.to }),
			})),
		},
	]
})
</script>
