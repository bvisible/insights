import { createRouter, createWebHistory, RouteLocation } from 'vue-router'
import session from './session.ts'

const routes = [
	{
		path: '/login',
		name: 'Login',
		component: () => import('./auth/Login.vue'),
		meta: { isGuestView: true, hideSidebar: true },
	},
	{
		path: '/',
		name: 'Home',
		redirect: '/dashboards',
		component: () => import('./home/Home.vue'),
	},
	{
		path: '/dashboards',
		name: 'DashboardList',
		component: () => import('./dashboard/DashboardList.vue'),
	},
	{
		props: true,
		name: 'Dashboard',
		path: '/dashboards/:name',
		component: () => import('./dashboard/Dashboard.vue'),
	},
	{
		path: '/workbook',
		name: 'WorkbookList',
		component: () => import('./workbook/WorkbookList.vue'),
	},
	{
		props: true,
		name: 'Workbook',
		path: '/workbook/:workbook_name',
		component: () => import('./workbook/Workbook.vue'),
		meta: { hideSidebar: true },
		children: [
			{
				props: true,
				path: 'query/:query_name',
				name: 'WorkbookQuery',
				component: () => import('./workbook/WorkbookQuery.vue'),
			},
			{
				props: true,
				path: 'chart/:chart_name',
				name: 'WorkbookChart',
				component: () => import('./workbook/WorkbookChart.vue'),
			},
			{
				props: true,
				path: 'dashboard/:dashboard_name',
				name: 'WorkbookDashboard',
				component: () => import('./workbook/WorkbookDashboard.vue'),
			},
		],
	},
	{
		props: true,
		name: 'OpenTemplate',
		path: '/template/:app/:folder',
		component: () => import('./workbook/OpenTemplate.vue'),
		meta: { hideSidebar: true },
	},
	{
		path: '/data-source',
		name: 'DataSourceList',
		component: () => import('./data_source/DataSourceList.vue'),
	},
	{
		props: true,
		path: '/data-source/:name',
		name: 'DataSourceTableList',
		component: () => import('./data_source/DataSourceTableList.vue'),
	},
	{
		props: true,
		path: '/data-source/:data_source/:table_name',
		name: 'DataSourceTable',
		component: () => import('./data_source/DataSourceTable.vue'),
	},
	{
		path: '/data-store',
		name: 'DataStoreList',
		component: () => import('./data_store/DataStoreList.vue'),
	},
	{
		props: true,
		name: 'SharedChart',
		path: '/shared/chart/:chart_name',
		component: () => import('./charts/SharedChart.vue'),
		meta: {
			hideSidebar: true,
			isGuestView: true,
		},
	},
	{
		props: true,
		name: 'SharedDashboard',
		path: '/shared/dashboard/:dashboard_name',
		component: () => import('./dashboard/SharedDashboard.vue'),
		meta: {
			hideSidebar: true,
			isGuestView: true,
		},
	},
	//// Neoffice — added (maintenance#2651): where a signed-in account without an Insights role lands (auth/NoPermission.vue).
	{
		path: '/no-permission',
		name: 'NoPermission',
		component: () => import('./auth/NoPermission.vue'),
		meta: { hideSidebar: true },
	},
	{
		path: '/:pathMatch(.*)*',
		component: () => import('./auth/NotFound.vue'),
		meta: { hideSidebar: true },
	},
]

let router = createRouter({
	history: createWebHistory('/insights'),
	// @ts-ignore
	routes,
})

router.beforeEach(async (to, _, next) => {
	!session.initialized && (await session.initialize())

	if (to.meta.isGuestView && !session.isLoggedIn && to.name !== 'Login') {
		// if page is allowed for guest, and is not login page, allow
		return next()
	}

	// route to login page if not logged in
	if (!session.isLoggedIn) {
		// if in dev mode, open login page
		if (import.meta.env.DEV) {
			return to.fullPath === '/login' ? next() : next('/login')
		}
		// redirect to frappe login page, for oauth and signup
		window.location.href = '/login'
		return next(false)
	}

	//// Neoffice — upstream checks the sign-in only (maintenance#2651): an account without an Insights role opened a blank
	//// shell whose every call answered 403, with no message and no way out. It goes to a page that says so; a page open
	//// to guests (a shared chart or dashboard) stays open to it, since a signed-in account never sees less than a guest.
	if (!session.isAuthorized && !to.meta.isGuestView && to.name !== 'NoPermission') {
		return next('/no-permission')
	}
	if (session.isAuthorized && to.name === 'NoPermission') {
		return next('/')
	}

	to.path === '/login' ? next('/') : next()
})

const _fetch = window.fetch
window.fetch = async function () {
	// @ts-ignore
	const res = await _fetch(...arguments)
	if (res.status === 403 && (!document.cookie || document.cookie.includes('user_id=Guest'))) {
		session.resetSession()
		router.push('/login')
	}
	return res
}

export default router
