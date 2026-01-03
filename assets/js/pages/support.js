import UTILS from '../core/utils.js';

const initSearch = async () => {
    const response = await fetch('/api/support/faqs/');
    const faqs = response.ok ? await response.json() : [];
    
    const searchInput = UTILS.qs('input[type="text"]');
    
    searchInput.addEventListener('input', (e) => {
        const term = e.target.value.toLowerCase();
        if(term.length < 2) return;

        const results = faqs.filter(f => 
            f.title.toLowerCase().includes(term) || 
            f.content.toLowerCase().includes(term)
        );

        // Logic to show results dropdown or redirect to search page
        console.log('Found:', results);
    });
};

initSearch();