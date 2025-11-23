/**
 * AI-102 Study Guide Content Extractor
 *
 * INSTRUCTIONS:
 * 1. Open https://learn.microsoft.com/en-us/credentials/certifications/resources/study-guides/ai-102
 * 2. Open browser Developer Tools (F12)
 * 3. Go to Console tab
 * 4. Copy and paste this entire script
 * 5. Press Enter to execute
 * 6. The script will output JSON that you can copy
 * 7. Save the output to a file named 'ai102_raw_data.json'
 */

(function extractAI102StudyGuide() {
    console.log('Starting AI-102 Study Guide Extraction...');

    const extractedData = {
        metadata: {
            exam_code: 'AI-102',
            exam_title: '',
            extraction_date: new Date().toISOString(),
            source_url: window.location.href,
            exam_update_date: ''
        },
        topic_areas: [],
        change_log: []
    };

    try {
        // Extract exam title
        const titleElement = document.querySelector('h1, .title, [data-bi-name="title"]');
        if (titleElement) {
            extractedData.metadata.exam_title = titleElement.textContent.trim();
        }

        // Look for exam update date
        const updateDateElement = document.querySelector('.content-header time, .updated-date, time');
        if (updateDateElement) {
            extractedData.metadata.exam_update_date = updateDateElement.getAttribute('datetime') || updateDateElement.textContent.trim();
        }

        // Method 1: Try to find main content area
        let mainContent = document.querySelector('main, article, .content, #main-content, [role="main"]');

        if (!mainContent) {
            mainContent = document.body;
        }

        // Find all headings that represent topic areas (usually h2 or h3)
        const headings = mainContent.querySelectorAll('h2, h3');
        let currentTopicArea = null;
        let currentSkill = null;

        headings.forEach((heading, index) => {
            const headingText = heading.textContent.trim();

            // Check if this is a topic area (contains percentage)
            const percentageMatch = headingText.match(/\((\d+[-–]\d+%)\)/);

            if (percentageMatch) {
                // This is a topic area
                const cleanTitle = headingText.replace(/\((\d+[-–]\d+%)\)/, '').trim();
                currentTopicArea = {
                    topic_area: cleanTitle,
                    percentage_weight: percentageMatch[1],
                    skills: []
                };
                extractedData.topic_areas.push(currentTopicArea);
                currentSkill = null;
            } else if (currentTopicArea && heading.tagName === 'H3') {
                // This might be a skill under current topic area
                currentSkill = {
                    skill: headingText,
                    sub_skills: []
                };
                currentTopicArea.skills.push(currentSkill);
            }

            // Find lists (ul, ol) following this heading
            let nextElement = heading.nextElementSibling;
            while (nextElement && !['H1', 'H2', 'H3'].includes(nextElement.tagName)) {
                if (nextElement.tagName === 'UL' || nextElement.tagName === 'OL') {
                    const listItems = nextElement.querySelectorAll('li');
                    listItems.forEach(li => {
                        const subSkillText = li.textContent.trim();

                        // Extract any links
                        const links = Array.from(li.querySelectorAll('a')).map(a => a.href);

                        if (currentSkill) {
                            currentSkill.sub_skills.push({
                                sub_skill: subSkillText,
                                reference_links: links,
                                annotation: ''
                            });
                        }
                    });
                }
                nextElement = nextElement.nextElementSibling;
            }
        });

        // Extract change log section
        const changeLogSection = Array.from(mainContent.querySelectorAll('h2, h3')).find(h =>
            /change/i.test(h.textContent) && /log/i.test(h.textContent)
        );

        if (changeLogSection) {
            let changeElement = changeLogSection.nextElementSibling;
            while (changeElement && !['H1', 'H2'].includes(changeElement.tagName)) {
                if (changeElement.tagName === 'TABLE') {
                    const rows = changeElement.querySelectorAll('tr');
                    rows.forEach((row, idx) => {
                        if (idx === 0) return; // Skip header
                        const cells = row.querySelectorAll('td, th');
                        if (cells.length >= 2) {
                            extractedData.change_log.push({
                                change_description: cells[0]?.textContent.trim() || '',
                                change_date: cells[1]?.textContent.trim() || '',
                                change_type: cells[2]?.textContent.trim() || 'Update'
                            });
                        }
                    });
                } else if (changeElement.tagName === 'UL' || changeElement.tagName === 'OL') {
                    const items = changeElement.querySelectorAll('li');
                    items.forEach(li => {
                        extractedData.change_log.push({
                            change_description: li.textContent.trim(),
                            change_date: extractedData.metadata.exam_update_date || 'Unknown',
                            change_type: 'Update'
                        });
                    });
                }
                changeElement = changeElement.nextElementSibling;
            }
        }

        // Output results
        console.log('Extraction Complete!');
        console.log('Topic Areas Found:', extractedData.topic_areas.length);
        console.log('Change Log Entries:', extractedData.change_log.length);
        console.log('\n=== COPY THE JSON BELOW ===\n');
        console.log(JSON.stringify(extractedData, null, 2));
        console.log('\n=== END OF JSON ===\n');

        // Also try to download as file
        try {
            const blob = new Blob([JSON.stringify(extractedData, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'ai102_raw_data.json';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            console.log('File download initiated!');
        } catch (e) {
            console.log('Auto-download failed, please copy JSON manually');
        }

        return extractedData;

    } catch (error) {
        console.error('Extraction Error:', error);
        console.log('Please copy the page HTML and use the HTML parser instead');
    }
})();
