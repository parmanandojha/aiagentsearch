let allBusinesses = [];
let filteredBusinesses = [];

// Load JSON data on page load
async function loadData() {
    try {
        const response = await fetch('/static/results.json');
        if (!response.ok) {
            // If results.json doesn't exist, that's OK - user hasn't searched yet
            return;
        }
        const data = await response.json();
        
        // Validate data structure
        if (!data.summary || !data.businesses) {
            console.log('Invalid results.json format');
            return;
        }
        
        // Update header
        document.getElementById('summary-info').textContent = 
            `${data.summary.industry} in ${data.summary.location}`;
        
        // Display summary
        displaySummary(data.summary);
        
        // Store businesses
        allBusinesses = data.businesses;
        filteredBusinesses = [...allBusinesses];
        
        // Display table
        displayTable(filteredBusinesses);
    } catch (error) {
        // Silently fail if no results.json - this is normal on first visit
        // Don't log errors for 404s as it's expected behavior
    }
}

function displaySummary(summary) {
    const summaryCards = document.getElementById('summary-cards');
    if (!summaryCards) {
        console.error('Summary cards element not found');
        return;
    }
    
    const cardsHtml = `
        <div class="summary-card">
            <h3>Total Businesses</h3>
            <div class="value">${summary.total_businesses || 0}</div>
        </div>
        <div class="summary-card">
            <h3>Poor Websites</h3>
            <div class="value">${summary.poor_websites_percentage || 0}%</div>
        </div>
        <div class="summary-card">
            <h3>Industry</h3>
            <div class="value" style="font-size: 1.2em;">${escapeHtml(summary.industry || 'N/A')}</div>
        </div>
        <div class="summary-card">
            <h3>Location</h3>
            <div class="value" style="font-size: 1.2em;">${escapeHtml(summary.location || 'N/A')}</div>
        </div>
    `;
    summaryCards.innerHTML = cardsHtml;
}

function displayTable(businesses) {
    const tbody = document.getElementById('table-body');
    if (!tbody) {
        console.error('Table body element not found');
        return;
    }
    
    if (!businesses || businesses.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="empty-state">
                    <h2>No businesses found</h2>
                    <p>Try adjusting your filters</p>
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = businesses.map((business, index) => {
        return getBusinessRowHtml(business, index);
    }).join('');
}

function getBusinessRowHtml(business, index) {
    const scoreClass = getScoreClass(business.website_score);
    const opportunityClass = getOpportunityClass(business.opportunity_level);
    
    return `
        <tr data-index="${index}">
            <td class="business-name">${escapeHtml(business.name)}</td>
            <td>
                ${business.website ? 
                    `<a href="${business.website}" target="_blank" class="website-link">${escapeHtml(business.website)}</a>` 
                    : '<span style="color: #999;">Not available</span>'}
            </td>
            <td>${escapeHtml(business.location || 'Unknown')}</td>
            <td>
                <span class="score-badge ${scoreClass}">
                    ${business.website_score}/10
                </span>
            </td>
            <td>
                <span class="opportunity-badge ${opportunityClass}">
                    ${business.opportunity_level}
                </span>
            </td>
            <td>
                <button class="expand-btn" onclick="toggleDetails(${index})">
                    View Details
                </button>
            </td>
        </tr>
        <tr class="details-row" data-index="${index}" style="display: none;">
            <td colspan="6">
                <div class="details-panel active">
                    ${getDetailsHtml(business)}
                </div>
            </td>
        </tr>
    `;
}

function appendBusinessRow(business, index) {
    const tbody = document.getElementById('table-body');
    if (!tbody) {
        console.error('Table body element not found');
        return;
    }
    
    // Remove empty state if present
    const emptyState = tbody.querySelector('.empty-state');
    if (emptyState) {
        emptyState.closest('tr').remove();
    }
    
    // Create temporary container to parse HTML
    const temp = document.createElement('tbody');
    temp.innerHTML = getBusinessRowHtml(business, index);
    
    // Append both rows (main row and details row)
    while (temp.firstChild) {
        tbody.appendChild(temp.firstChild);
    }
}

function getDetailsHtml(business) {
    const contact = business.contact || {};
    const socials = business.socials || {};
    const tech = business.tech_stack || {};
    const issues = business.issues || [];

    const socialLinks = [];
    if (socials.instagram) socialLinks.push(`<a href="${socials.instagram}" target="_blank" class="social-link">Instagram</a>`);
    if (socials.facebook) socialLinks.push(`<a href="${socials.facebook}" target="_blank" class="social-link">Facebook</a>`);
    if (socials.linkedin) socialLinks.push(`<a href="${socials.linkedin}" target="_blank" class="social-link">LinkedIn</a>`);
    if (socials.twitter) socialLinks.push(`<a href="${socials.twitter}" target="_blank" class="social-link">Twitter</a>`);
    if (socials.youtube) socialLinks.push(`<a href="${socials.youtube}" target="_blank" class="social-link">YouTube</a>`);

    const analytics = Array.isArray(tech.analytics) ? tech.analytics.join(', ') : (tech.analytics || 'None');

    return `
        <div class="details-grid">
            <div class="detail-section">
                <h4>Contact Information</h4>
                <p><strong>Phone:</strong> ${contact.phone || 'Not found'}</p>
                <p><strong>Email:</strong> ${contact.email || 'Not found'}</p>
                ${contact.contact_form ? `<p><strong>Contact Form:</strong> <a href="${contact.contact_form}" target="_blank">${contact.contact_form}</a></p>` : ''}
            </div>

            <div class="detail-section">
                <h4>Social Media</h4>
                ${socialLinks.length > 0 ? 
                    `<div class="social-links">${socialLinks.join('')}</div>` : 
                    '<p style="color: #999;">No social media links found</p>'}
            </div>

            <div class="detail-section">
                <h4>Tech Stack</h4>
                <p><strong>CMS:</strong> ${tech.cms || 'Not detected'}</p>
                <p><strong>Frontend:</strong> ${tech.frontend || 'Not detected'}</p>
                <p><strong>Analytics:</strong> ${analytics}</p>
            </div>

            <div class="detail-section">
                <h4>Issues Found</h4>
                ${issues.length > 0 ? 
                    `<ul class="issues-list">${issues.map(issue => `<li>${escapeHtml(issue)}</li>`).join('')}</ul>` : 
                    '<p style="color: #28a745;">✅ No major issues detected</p>'}
            </div>
        </div>
    `;
}

function toggleDetails(index) {
    console.log('Toggle details called for index:', index);
    
    // Find all rows with the matching data-index
    const allRows = document.querySelectorAll(`tbody tr[data-index="${index}"]`);
    const detailsRow = document.querySelector(`tr.details-row[data-index="${index}"]`);
    
    if (!detailsRow) {
        console.error('Details row not found for index:', index);
        return;
    }
    
    // Find the main row (not the details row)
    let mainRow = null;
    for (let row of allRows) {
        if (!row.classList.contains('details-row')) {
            mainRow = row;
            break;
        }
    }
    
    if (!mainRow) {
        console.error('Main row not found for index:', index);
        return;
    }
    
    const button = mainRow.querySelector('.expand-btn');
    if (!button) {
        console.error('Button not found for index:', index);
        return;
    }
    
    // Toggle visibility
    if (detailsRow.style.display === 'none' || !detailsRow.style.display || detailsRow.style.display === '') {
        detailsRow.style.display = 'table-row';
        mainRow.classList.add('expanded');
        button.textContent = 'Hide Details';
        console.log('Details shown for index:', index);
    } else {
        detailsRow.style.display = 'none';
        mainRow.classList.remove('expanded');
        button.textContent = 'View Details';
        console.log('Details hidden for index:', index);
    }
}

function filterTable() {
    const searchTerm = document.getElementById('search-input').value.toLowerCase();
    const opportunityFilter = document.getElementById('opportunity-filter').value;
    const scoreFilter = document.getElementById('score-filter').value;

    filteredBusinesses = allBusinesses.filter(business => {
        // Text search
        const matchesSearch = !searchTerm || 
            business.name.toLowerCase().includes(searchTerm) ||
            (business.website && business.website.toLowerCase().includes(searchTerm)) ||
            (business.location && business.location.toLowerCase().includes(searchTerm));

        // Opportunity filter
        const matchesOpportunity = !opportunityFilter || 
            business.opportunity_level === opportunityFilter;

        // Score filter
        let matchesScore = true;
        if (scoreFilter === 'high') {
            matchesScore = business.website_score >= 7;
        } else if (scoreFilter === 'medium') {
            matchesScore = business.website_score >= 4 && business.website_score < 7;
        } else if (scoreFilter === 'low') {
            matchesScore = business.website_score < 4;
        }

        return matchesSearch && matchesOpportunity && matchesScore;
    });

    displayTable(filteredBusinesses);
}

function getScoreClass(score) {
    if (score >= 7) return 'score-high';
    if (score >= 4) return 'score-medium';
    return 'score-low';
}

function getOpportunityClass(level) {
    if (level === 'High Potential') return 'opportunity-high';
    if (level === 'Digitally Mature') return 'opportunity-mature';
    return 'opportunity-redesign';
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

let currentEventSource = null;

async function runNewSearch(event) {
    event.preventDefault();
    
    const industry = document.getElementById('industry-input').value.trim();
    const location = document.getElementById('location-input').value.trim();
    const maxResultsInput = document.getElementById('max-results-input');
    let maxResults = parseInt(maxResultsInput.value) || 50;
    
    // Validate max results
    if (maxResults < 1) {
        maxResults = 1;
        maxResultsInput.value = 1;
    } else if (maxResults > 100) {
        maxResults = 100;
        maxResultsInput.value = 100;
    }
    
    const searchBtn = document.getElementById('search-btn');
    const statusDiv = document.getElementById('search-status');
    
    if (!industry || !location) {
        statusDiv.className = 'search-status error';
        statusDiv.textContent = 'Please fill in both industry and location';
        return;
    }
    
    // Close any existing event source
    if (currentEventSource) {
        currentEventSource.close();
        currentEventSource = null;
    }
    
    // Clear existing businesses and summary
    allBusinesses = [];
    filteredBusinesses = [];
    
    // Clear table body
    const tbody = document.getElementById('table-body');
    if (tbody) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="empty-state">
                    <h2>Searching...</h2>
                    <p>Results will appear as they are found</p>
                </td>
            </tr>
        `;
    }
    
    // Clear summary cards
    const summaryCards = document.getElementById('summary-cards');
    if (summaryCards) {
        summaryCards.innerHTML = '';
    }
    
    // Disable button and show loading
    searchBtn.disabled = true;
    searchBtn.textContent = 'Searching...';
    statusDiv.className = 'search-status loading';
    statusDiv.innerHTML = `🔍 Searching for "${industry}" in "${location}"... Results will appear as they are found.`;
    
    // Update header
    document.getElementById('summary-info').textContent = `${industry} in ${location}`;
    
    // Make sure summary and table sections are visible
    const summarySection = document.getElementById('summary-section');
    if (summarySection) {
        summarySection.style.display = 'block';
    }
    const tableContainer = document.querySelector('.table-container');
    if (tableContainer) {
        tableContainer.style.display = 'block';
    }
    
    try {
        const requestData = {
            industry: industry,
            location: location,
            max_results: maxResults
        };
        
        // Use POST request to send data, then use EventSource for streaming
        // We need to use a different approach - send POST data as query params or use a token
        // For simplicity, we'll use POST with fetch first, then switch to SSE
        // Actually, we need to use POST for the initial request. Let's use fetch with a streaming endpoint
        
        const response = await fetch('/api/search/stream', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(requestData)
        });
        
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Server error: ${response.status}. ${errorText.substring(0, 100)}`);
        }
        
        // Parse Server-Sent Events from the stream
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        let currentEvent = null;
        let currentData = null;
        
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop() || ''; // Keep incomplete line in buffer
            
            for (const line of lines) {
                if (line.startsWith('event: ')) {
                    currentEvent = line.substring(7).trim();
                } else if (line.startsWith('data: ')) {
                    currentData = line.substring(6).trim();
                } else if (line.trim() === '') {
                    // Empty line indicates end of message
                    if (currentData) {
                        try {
                            const data = JSON.parse(currentData);
                            handleStreamEvent(currentEvent, data);
                        } catch (e) {
                            console.error('Error parsing SSE data:', e, currentData);
                        }
                    }
                    currentEvent = null;
                    currentData = null;
                }
            }
        }
        
        // Handle any remaining data in buffer
        if (currentData) {
            try {
                const data = JSON.parse(currentData);
                handleStreamEvent(currentEvent, data);
            } catch (e) {
                console.error('Error parsing final SSE data:', e);
            }
        }
        
    } catch (error) {
        statusDiv.className = 'search-status error';
        statusDiv.textContent = `❌ Error: ${error.message}`;
        console.error('Search error:', error);
        searchBtn.disabled = false;
        searchBtn.textContent = 'Run Search';
    }
}

function handleStreamEvent(eventType, data) {
    const statusDiv = document.getElementById('search-status');
    const searchBtn = document.getElementById('search-btn');
    
    console.log('SSE Event:', eventType, data);
    
    if (eventType === 'error' || data.error) {
        statusDiv.className = 'search-status error';
        statusDiv.textContent = `❌ Error: ${data.error || 'Unknown error'}`;
        searchBtn.disabled = false;
        searchBtn.textContent = 'Run Search';
        return;
    }
    
    if (eventType === 'business' && data.business) {
        // Add business to arrays
        const index = allBusinesses.length;
        allBusinesses.push(data.business);
        filteredBusinesses.push(data.business);
        
        // Append to table
        appendBusinessRow(data.business, index);
        
        // Update status
        statusDiv.className = 'search-status loading';
        statusDiv.innerHTML = `🔍 Found ${data.index}/${data.total} businesses... Keep searching!`;
        
        // Scroll to latest result (scroll to last row, but not too aggressively)
        if (index % 5 === 0 || index === data.total - 1) {
            setTimeout(() => {
                const tbody = document.getElementById('table-body');
                if (tbody && tbody.lastChild) {
                    tbody.lastChild.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                }
            }, 100);
        }
    }
    
    if (eventType === 'summary' && data.summary) {
        // Update summary cards
        displaySummary(data.summary);
        
        // Update header
        document.getElementById('summary-info').textContent = 
            `${data.summary.industry} in ${data.summary.location}`;
    }
    
    if (eventType === 'complete') {
        // Search complete
        statusDiv.className = 'search-status success';
        statusDiv.textContent = `✅ ${data.message || 'Search complete!'}`;
        searchBtn.disabled = false;
        searchBtn.textContent = 'Run Search';
        
        // Scroll to table
        setTimeout(() => {
            const tableContainer = document.querySelector('.table-container');
            if (tableContainer) {
                tableContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        }, 100);
    }
    
    if (eventType === 'progress' && data.current) {
        // Update progress
        statusDiv.className = 'search-status loading';
        statusDiv.innerHTML = `🔍 ${data.message || `Processing ${data.current}/${data.total} businesses...`}`;
    }
    
    if (eventType === 'status') {
        // Update status message
        statusDiv.className = 'search-status loading';
        statusDiv.textContent = data.message || 'Processing...';
    }
    
    if (eventType === 'rate_limit_info') {
        // Store next allowed time in localStorage
        if (data.next_allowed_time) {
            localStorage.setItem('rateLimitNextAllowed', data.next_allowed_time);
            console.log('Rate limit info stored:', data.next_allowed_time);
        }
    }
}

// Countdown timer for rate limit
function updateRateLimitCountdown() {
    const stored = localStorage.getItem('rateLimitNextAllowed');
    if (!stored) {
        // No rate limit stored, hide countdown
        const countdownEl = document.getElementById('rate-limit-countdown');
        if (countdownEl) {
            countdownEl.style.display = 'none';
        }
        return;
    }
    
    const nextAllowed = new Date(stored);
    const now = new Date();
    const timeLeft = nextAllowed - now;
    
    const countdownEl = document.getElementById('rate-limit-countdown');
    if (!countdownEl) return;
    
    if (timeLeft <= 0) {
        // Rate limit expired
        countdownEl.style.display = 'none';
        localStorage.removeItem('rateLimitNextAllowed');
        // Enable search button if it exists
        const searchBtn = document.getElementById('search-btn');
        if (searchBtn) {
            searchBtn.disabled = false;
        }
        return;
    }
    
    // Calculate time components
    const hours = Math.floor(timeLeft / (1000 * 60 * 60));
    const minutes = Math.floor((timeLeft % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((timeLeft % (1000 * 60)) / 1000);
    
    // Display countdown
    countdownEl.style.display = 'block';
    countdownEl.innerHTML = `⏱️ Rate Limit: Next request allowed in <strong>${hours}h ${minutes}m ${seconds}s</strong>`;
    
    // Disable search button if it exists
    const searchBtn = document.getElementById('search-btn');
    if (searchBtn) {
        searchBtn.disabled = true;
    }
}

// Update countdown every second
setInterval(updateRateLimitCountdown, 1000);

// Helper function to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Load data on page load
document.addEventListener('DOMContentLoaded', function() {
    loadData();
    updateRateLimitCountdown(); // Initialize countdown timer
});

