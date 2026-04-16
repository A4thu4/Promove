import { SimulatorProvider } from '@/context/simulator-context';
import { SimulatorForm }     from '@/components/simulator/SimulatorForm';
import Navbar                from '@/components/navbar';

export default function Home() {
  return (
    <>
      <Navbar />
      <main className="max-w-6xl mx-auto px-4 py-6">
        <header className="mb-6 text-center">
          <h1 className="text-3xl font-bold text-gray-900">
            PROMOVE — Simulador de Evoluções Funcionais
          </h1>
          <p className="text-gray-500 mt-1 text-sm">
            Poder Executivo do Estado de Goiás
          </p>
        </header>

        <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg text-yellow-800 text-sm text-center">
          ⚠️ Ferramenta de simulação. Os resultados não têm valor oficial.
        </div>

        <SimulatorProvider>
          <SimulatorForm />
        </SimulatorProvider>
      </main>
    </>
  );
}