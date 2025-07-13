import {defineConfig, loadEnv} from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig(async ({mode}) => {
    // eslint-disable-next-line no-undef
    const env = loadEnv(mode, process.cwd());
    const domainName = env.VITE_DOMAIN_NAME;

    return {
        plugins: [react()],
        server: {allowedHosts: ['localhost', '127.0.0.1', '0.0.0.0', domainName],}
    }
})