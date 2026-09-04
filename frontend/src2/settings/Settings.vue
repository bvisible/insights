<script setup lang="ts">
import { Building2, CircleUser, DatabaseZap, KeyRound, SettingsIcon, Users } from 'lucide-vue-next'
import { defineAsyncComponent, shallowRef } from 'vue'
import TabbedSidebarLayout, { Tab, TabGroup } from '../components/TabbedSidebarLayout.vue'
//// Neoffice — added import. The whole file's user-facing strings are wrapped in
//// __() (upstream hardcodes English); the French catalogue lives in
//// insights/locale/fr.po. Keep this import when merging upstream's version.
import { __ } from '../translation'

const showDialog = defineModel({ required: true, default: false })
const tabGroups: TabGroup[] = [
	{
		//// Neoffice — __() wrapping: upstream hardcodes English, our fleet is French
		groupLabel: __('Account'),
		tabs: [
			{
				//// Neoffice — __() wrapping: upstream hardcodes English, our fleet is French
				label: __('Profile'),
				icon: CircleUser,
				component: defineAsyncComponent(() => import('./ProfileSettings.vue')),
			},
		],
	},
	{
		//// Neoffice — __() wrapping: upstream hardcodes English, our fleet is French
		groupLabel: __('Organization'),
		tabs: [
			{
				//// Neoffice — __() wrapping: upstream hardcodes English, our fleet is French
				label: __('General'),
				icon: SettingsIcon,
				component: defineAsyncComponent(() => import('./GeneralSettings.vue')),
			},
			// {
			// 	label: 'Email Accounts',
			// 	icon: Mail,
			// 	component: () => {},
			// },
			{
				//// Neoffice — __() wrapping: upstream hardcodes English, our fleet is French
				label: __('Users'),
				icon: Users,
				component: defineAsyncComponent(() => import('./UsersSettings.vue')),
			},
			{
				//// Neoffice — __() wrapping: upstream hardcodes English, our fleet is French
				label: __('Permissions'),
				icon: KeyRound,
				component: defineAsyncComponent(() => import('./PermissionsSettings.vue')),
			},
			{
				//// Neoffice — __() wrapping: upstream hardcodes English, our fleet is French
				label: __('Data Store'),
				icon: DatabaseZap,
				component: defineAsyncComponent(() => import('./DataStoreSettings.vue')),
			},
		],
	},
]
const activeTab = shallowRef<Tab>(tabGroups[0].tabs[0])
</script>

<template>
	<Dialog v-model="showDialog" :options="{ size: '4xl' }">
		<template #body>
			<div class="relative flex text-base" :style="{ height: 'calc(100vh - 12rem)' }">
				<!-- //// Neoffice — __() wrapping: upstream hardcodes English, our fleet is French -->
				<TabbedSidebarLayout
					:title="__('Settings')"
					:tabs="tabGroups"
					v-model:activeTab="activeTab"
				/>
			</div>
		</template>
	</Dialog>
</template>
