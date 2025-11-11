import { useState, useEffect } from 'react';
import './App.css';

interface Dog {
    id?: number;
    breed: string;
    image?: string;
}

interface DogPageData {
    dogs: Dog[];
    page: number;
    total_dogs: number;
    total_pages: number;
}

function App() {
    // Get initial page from URL query parameter
    const getInitialPage = () => {
        const urlParams = new URLSearchParams(window.location.search);
        const pageParam = urlParams.get('page');
        const page = pageParam ? parseInt(pageParam, 10) : 1;
        return isNaN(page) || page < 1 ? 1 : page;
    };

    const [dogData, setDogData] = useState<DogPageData | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [currentPage, setCurrentPage] = useState(getInitialPage());

    const fetchDogs = async (page: number) => {
        setLoading(true);
        setError(null);
        try {
            // Use environment variable or default to localhost for development
            const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
            const response = await fetch(`${apiUrl}/dogs?page=${page}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data: DogPageData = await response.json();
            setDogData(data);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchDogs(currentPage);
    }, [currentPage]);

    const handlePageChange = (page: number) => {
        setCurrentPage(page);
        // Update URL with page parameter
        const url = new URL(window.location.href);
        if (page === 1) {
            url.searchParams.delete('page');
        } else {
            url.searchParams.set('page', page.toString());
        }
        window.history.replaceState({}, '', url.toString());
    };

    const renderPagination = () => {
        if (!dogData) return null;

        const { total_pages, page } = dogData;
        const pages = [];

        // Show max 5 pages around current page
        const startPage = Math.max(1, page - 2);
        const endPage = Math.min(total_pages, page + 2);

        for (let i = startPage; i <= endPage; i++) {
            pages.push(
                <button key={i} onClick={() => handlePageChange(i)} className={`page-button ${i === page ? 'active' : ''}`}>
                    {i}
                </button>,
            );
        }

        return (
            <div className='pagination'>
                <button onClick={() => handlePageChange(page - 1)} disabled={page <= 1} className='page-button'>
                    ‹ Previous
                </button>
                {pages}
                <button onClick={() => handlePageChange(page + 1)} disabled={page >= total_pages} className='page-button'>
                    Next ›
                </button>
            </div>
        );
    };

    return (
        <div className='app'>
            <header className='header'>
                <h1>🐕 DogeDB - Discover Dog Breeds</h1>
                <p>Explore our collection of amazing dog breeds</p>
            </header>

            <main className='main'>
                {loading && <div className='loading'>🐕 Loading dogs...</div>}

                {error && <div className='error'>🐶 Error: {error}</div>}

                {dogData && dogData.total_dogs === 0 && !loading && (
                    <div className='seeding-message'>
                        <div className='seeding-content'>
                            <div className='doge-face'>🐕</div>
                            <h2>Wow! Such Empty!</h2>
                            <p>Our dog database is still loading all the amazing breeds. Please wait a moment and refresh the page.</p>
                            <button onClick={() => fetchDogs(currentPage)} className='retry-button'>
                                🔄 Retry Loading Dogs
                            </button>
                        </div>
                    </div>
                )}

                {dogData && dogData.total_dogs > 0 && (
                    <>
                        <div className='stats'>
                            Showing {dogData.dogs.length} dogs • Page {dogData.page} of {dogData.total_pages} • Total: {dogData.total_dogs} breeds
                        </div>

                        <div className='dogs-grid'>
                            {dogData.dogs.map((dog, index) => (
                                <div key={dog.id || index} className='dog-card'>
                                    {dog.image ? (
                                        <img
                                            src={dog.image}
                                            alt={`${dog.breed} dog`}
                                            className='dog-image'
                                            onError={e => {
                                                (e.target as HTMLImageElement).src = 'https://i.imgflip.com/40i6rq.jpg';
                                            }}
                                        />
                                    ) : (
                                        <div className='no-image'></div>
                                    )}
                                    <div className='dog-info'>
                                        <h3 className='dog-breed'>{dog.breed}</h3>
                                    </div>
                                </div>
                            ))}
                        </div>

                        {renderPagination()}
                    </>
                )}
            </main>

            <footer className='footer'>
                <p>Built with ❤️ and 💩 for dog lovers everywhere</p>
            </footer>
        </div>
    );
}

export default App;
