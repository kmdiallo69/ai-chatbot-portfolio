import dynamic from 'next/dynamic'

const App = dynamic(() => import("../components/app"), {
  ssr: false,
  loading: () => <div>Loading...</div>
});

const Index = () => <App />;
export default Index;