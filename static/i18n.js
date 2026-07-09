const translations = {
    'English': {
        // Sidebar navigation
        'nav_dashboard': 'Dashboard',
        'nav_transactions': 'Transactions',
        'nav_calendar': 'Calendar',
        'nav_reports': 'Reports',
        'nav_settings': 'Settings',
        'logout_btn': 'Logout',
        'search_placeholder': 'Search...',

        // Dashboard (index.html)
        'dash_title': 'Dashboard',
        'dash_btn_add_tx': 'Add Transaction',
        'card_total_balance': 'Total Balance',
        'card_total_income': 'Total Income',
        'card_total_spent': 'Total Expenses',
        'card_spending_ratio': 'Spending Ratio',
        'chart_monthly_spending': 'Monthly Spending',
        'chart_spending_label': 'Spending',
        'recent_activity': 'Recent Transactions',
        'no_transactions': 'No transactions found',
        'loading_tx': 'Loading transactions...',
        'warn_exceeded': 'Warning: Budget Threshold Exceeded!',
        'warn_exceeded_desc': 'Your monthly spending has reached $RATIO of your budget. Consider reducing unnecessary expenses.',

        // Transactions (transactions.html)
        'tx_title': 'Add Transactions',
        'tx_card_income': 'Add Money (Income)',
        'tx_source': 'Source',
        'tx_amount': 'Amount',
        'tx_source_placeholder': 'e.g., Salary, Freelance',
        'tx_btn_add_income': 'Add Income',
        'tx_card_expense': 'Add Expense (Spent)',
        'tx_category': 'Category',
        'tx_select_category': 'Select a category',
        'tx_custom_category': 'New Category Name',
        'tx_custom_placeholder': 'Enter category name',
        'tx_recurring_bill': 'Is this a recurring bill?',
        'tx_btn_add_expense': 'Add Expense',

        // Calendar (calendar.html)
        'cal_title': 'Financial Calendar',
        'cal_money_added': 'Money Added (Income)',
        'cal_money_spent': 'Money Spent (Expense)',
        'cal_both': 'Both Inflow & Outflow',
        'cal_details': 'Activity Details',
        'cal_click_inspect': 'Click on any calendar day to inspect transactions',
        'cal_set_reminder': 'Set Bill / Pending Payment Reminder',
        'cal_rem_desc': 'Description (e.g. Internet Bill)',
        'cal_rem_amount': 'Amount (optional)',
        'cal_save_reminder': 'Save Reminder',
        'cal_scheduled': 'Scheduled Reminders & Bills',
        'cal_loading_reminders': 'Loading reminders...',
        'cal_no_reminders': 'No scheduled reminders.',

        // Reports (reports.html)
        'rep_title': 'Financial Reports',
        'rep_select_month': 'Select Month',
        'rep_breakdown': 'Spending Breakdown',
        'rep_history': 'Transaction History',
        'rep_no_spending': 'No spending recorded for this month.',
        'rep_no_tx': 'No transactions recorded for this month',
        'rep_download_btn': 'Download Project Report',

        // Settings (settings.html)
        'set_title': 'Settings',
        'set_profile': 'Profile Details',
        'set_name': 'Name',
        'set_age': 'Age',
        'set_gender': 'Gender',
        'set_gender_select': 'Select...',
        'set_male': 'Male',
        'set_female': 'Female',
        'set_gender_other': 'Other',
        'set_phone': 'Phone Number',
        'set_profession': 'Profession',
        'set_profession_select': 'Select...',
        'set_student': 'Student',
        'set_professional': 'Working Professional',
        'set_business': 'Business',
        'set_freelancer': 'Freelancer',
        'set_profession_other': 'Other',
        'set_address': 'Address',
        'set_save_changes': 'Save Changes',
        'set_preferences': 'Preferences',
        'set_language': 'Language',
        'set_currency': 'Currency & Country',
        'set_theme': 'App Theme',
        'set_theme_light': 'Light Mode (Default)',
        'set_theme_dark': 'Dark Mode',
        'set_theme_blue': 'Ocean Blue',
        'set_theme_green': 'Forest Green',
        'set_notifications': 'Push Notifications',
        'set_notifications_desc': 'Receive alerts for bills and budget limits',
        'set_security': 'Security',
        'set_new_password': 'New Password',
        'set_update_password': 'Update Password',
        'set_save_all': 'Save All Settings',
        'set_placeholder_name': 'Enter your name',
        'set_placeholder_phone': 'Phone Number',
        'set_placeholder_address': 'Your address',
        'set_placeholder_password': 'Enter new password',
        
        // Categories
        'Food & Dining': 'Food & Dining',
        'Shopping': 'Shopping',
        'Transport': 'Transport',
        'Bills & Utilities': 'Bills & Utilities',
        'Entertainment': 'Entertainment',
        'Other': 'Other'
    },
    'Kannada': {
        // Sidebar navigation
        'nav_dashboard': 'ಡ್ಯಾಶ್‌ಬೋರ್ಡ್',
        'nav_transactions': 'ವಹಿವಾಟುಗಳು',
        'nav_calendar': 'ಕ್ಯಾಲೆಂಡರ್',
        'nav_reports': 'ವರದಿಗಳು',
        'nav_settings': 'ಸೆಟ್ಟಿಂಗ್‌ಗಳು',
        'logout_btn': 'ಲಾಗ್ ಔಟ್',
        'search_placeholder': 'ಹುಡುಕಿ...',

        // Dashboard (index.html)
        'dash_title': 'ಡ್ಯಾಶ್‌ಬೋರ್ಡ್',
        'dash_btn_add_tx': 'ವಹಿವಾಟು ಸೇರಿಸಿ',
        'card_total_balance': 'ಒಟ್ಟು ಬ್ಯಾಲೆನ್ಸ್',
        'card_total_income': 'ಒಟ್ಟು ಆದಾಯ',
        'card_total_spent': 'ಒಟ್ಟು ಖರ್ಚು',
        'card_spending_ratio': 'ಖರ್ಚು ಅನುಪಾತ',
        'chart_monthly_spending': 'ಮಾಸಿಕ ಖರ್ಚು',
        'chart_spending_label': 'ಖರ್ಚು',
        'recent_activity': 'ಇತ್ತೀಚಿನ ವಹಿವಾಟುಗಳು',
        'no_transactions': 'ಯಾವುದೇ ವಹಿವಾಟುಗಳು ಕಂಡುಬಂದಿಲ್ಲ',
        'loading_tx': 'ವಹಿವಾಟುಗಳನ್ನು ಲೋಡ್ ಮಾಡಲಾಗುತ್ತಿದೆ...',
        'warn_exceeded': 'ಎಚ್ಚರಿಕೆ: ಬಜೆಟ್ ಮಿತಿ ಮೀರಿದೆ!',
        'warn_exceeded_desc': 'ನಿಮ್ಮ ಮಾಸಿಕ ಖರ್ಚು ನಿಮ್ಮ ಬಜೆಟ್‌ನ $RATIO ತಲುಪಿದೆ. ಅನಗತ್ಯ ಖರ್ಚುಗಳನ್ನು ಕಡಿಮೆ ಮಾಡಲು ಪರಿಗಣಿಸಿ.',

        // Transactions (transactions.html)
        'tx_title': 'ವಹಿವಾಟು ಸೇರಿಸಿ',
        'tx_card_income': 'ಹಣ ಸೇರಿಸಿ (ಆದಾಯ)',
        'tx_source': 'ಮೂಲ',
        'tx_amount': 'ಮೊತ್ತ',
        'tx_source_placeholder': 'ಉದಾ: ಸಂಬಳ, ಸ್ವತಂತ್ರ ಉದ್ಯೋಗ',
        'tx_btn_add_income': 'ಆದಾಯ ಸೇರಿಸಿ',
        'tx_card_expense': 'ಖರ್ಚು ಸೇರಿಸಿ',
        'tx_category': 'ವರ್ಗ',
        'tx_select_category': 'ವರ್ಗವನ್ನು ಆಯ್ಕೆಮಾಡಿ',
        'tx_custom_category': 'ಹೊಸ ವರ್ಗದ ಹೆಸರು',
        'tx_custom_placeholder': 'ವರ್ಗದ ಹೆಸರನ್ನು ನಮೂದಿಸಿ',
        'tx_recurring_bill': 'ಇದು ಮರುಕಳಿಸುವ ಬಿಲ್ ಆಗಿದೆಯೇ?',
        'tx_btn_add_expense': 'ಖರ್ಚು ಸೇರಿಸಿ',

        // Calendar (calendar.html)
        'cal_title': 'ಹಣಕಾಸು ಕ್ಯಾಲೆಂಡರ್',
        'cal_money_added': 'ಹಣ ಸೇರಿಸಲಾಗಿದೆ (ಆದಾಯ)',
        'cal_money_spent': 'ಹಣ ಖರ್ಚು ಮಾಡಲಾಗಿದೆ (ಖರ್ಚು)',
        'cal_both': 'ಆದಾಯ ಮತ್ತು ಖರ್ಚು ಎರಡೂ',
        'cal_details': 'ಚಟುವಟಿಕೆಯ ವಿವರಗಳು',
        'cal_click_inspect': 'ವಹಿವಾಟುಗಳನ್ನು ಪರಿಶೀಲಿಸಲು ಯಾವುದೇ ಕ್ಯಾಲೆಂಡರ್ ದಿನದ ಮೇಲೆ ಕ್ಲಿಕ್ ಮಾಡಿ',
        'cal_set_reminder': 'ಬಿಲ್ / ಬಾಕಿ ಪಾವತಿ ಜ್ಞಾಪನೆ ಹೊಂದಿಸಿ',
        'cal_rem_desc': 'ವಿವರಣೆ (ಉದಾ: ಇಂಟರ್ನೆಟ್ ಬಿಲ್)',
        'cal_rem_amount': 'ಮೊತ್ತ (ಐಚ್ಛಿಕ)',
        'cal_save_reminder': 'ಜ್ಞಾಪನೆ ಉಳಿಸಿ',
        'cal_scheduled': 'ನಿಗದಿತ ಜ್ಞಾಪನೆಗಳು ಮತ್ತು ಬಿಲ್ಲುಗಳು',
        'cal_loading_reminders': 'ಜ್ಞಾಪನೆಗಳನ್ನು ಲೋಡ್ ಮಾಡಲಾಗುತ್ತಿದೆ...',
        'cal_no_reminders': 'ಯಾವುದೇ ಜ್ಞಾಪನೆಗಳಿಲ್ಲ.',

        // Reports (reports.html)
        'rep_title': 'ಹಣಕಾಸು ವರದಿಗಳು',
        'rep_select_month': 'ತಿಂಗಳು ಆಯ್ಕೆಮಾಡಿ',
        'rep_breakdown': 'ಖರ್ಚುಗಳ ವರ್ಗೀಕರಣ',
        'rep_history': 'ವಹಿವಾಟಿನ ಇತಿಹಾಸ',
        'rep_no_spending': 'ಈ ತಿಂಗಳಲ್ಲಿ ಯಾವುದೇ ಖರ್ಚು ದಾಖಲಾಗಿಲ್ಲ.',
        'rep_no_tx': 'ಈ ತಿಂಗಳಲ್ಲಿ ಯಾವುದೇ ವಹಿವಾಟುಗಳು ದಾಖಲಾಗಿಲ್ಲ',
        'rep_download_btn': 'ಯೋಜನೆಯ ವರದಿಯನ್ನು ಡೌನ್‌ಲೋಡ್ ಮಾಡಿ',

        // Settings (settings.html)
        'set_title': 'ಸೆಟ್ಟಿಂಗ್‌ಗಳು',
        'set_profile': 'ಪ್ರೊಫೈಲ್ ವಿವರಗಳು',
        'set_name': 'ಹೆಸರು',
        'set_age': 'ವಯಸ್ಸು',
        'set_gender': 'ಲಿಂಗ',
        'set_gender_select': 'ಆಯ್ಕೆಮಾಡಿ...',
        'set_male': 'ಪುರುಷ',
        'set_female': 'ಮಹಿಳೆ',
        'set_gender_other': 'ಇತರೆ',
        'set_phone': 'ದೂರವಾಣಿ ಸಂಖ್ಯೆ',
        'set_profession': 'ವೃತ್ತಿ',
        'set_profession_select': 'ಆಯ್ಕೆಮಾಡಿ...',
        'set_student': 'ವಿದ್ಯಾರ್ಥಿ',
        'set_professional': 'ಉದ್ಯೋಗಿ',
        'set_business': 'ವ್ಯಾಪಾರ',
        'set_freelancer': 'ಫ್ರೀಲ್ಯಾನ್ಸರ್',
        'set_profession_other': 'ಇತರೆ',
        'set_address': 'ವಿಳಾಸ',
        'set_save_changes': 'ಬದಲಾವಣೆಗಳನ್ನು ಉಳಿಸಿ',
        'set_preferences': 'ಆದ್ಯತೆಗಳು',
        'set_language': 'ಭಾಷೆ',
        'set_currency': 'ಕರೆನ್ಸಿ ಮತ್ತು ದೇಶ',
        'set_theme': 'ಅಪ್ಲಿಕೇಶನ್ ಥೀಮ್',
        'set_theme_light': 'ಲೈಟ್ ಮೋಡ್',
        'set_theme_dark': 'ಡಾರ್ಕ್ ಮೋಡ್',
        'set_theme_blue': 'ಸಾಗರ ನೀಲಿ',
        'set_theme_green': 'ಅರಣ್ಯ ಹಸಿರು',
        'set_notifications': 'ಪುಶ್ ಅಧಿಸೂಚನೆಗಳು',
        'set_notifications_desc': 'ಬಿಲ್ಲುಗಳು ಮತ್ತು ಬಜೆಟ್ ಮಿತಿಗಳಿಗಾಗಿ ಎಚ್ಚರಿಕೆಗಳನ್ನು ಸ್ವೀಕರಿಸಿ',
        'set_security': 'ಭದ್ರತೆ',
        'set_new_password': 'ಹೊಸ ಪಾಸ್‌ವರ್ಡ್',
        'set_update_password': 'ಪಾಸ್‌ವರ್ಡ್ ನವೀಕರಿಸಿ',
        'set_save_all': 'ಎಲ್ಲಾ ಸೆಟ್ಟಿಂಗ್‌ಗಳನ್ನು ಉಳಿಸಿ',
        'set_placeholder_name': 'ನಿಮ್ಮ ಹೆಸರನ್ನು ನಮೂದಿಸಿ',
        'set_placeholder_phone': 'ದೂರವಾಣಿ ಸಂಖ್ಯೆ',
        'set_placeholder_address': 'ನಿಮ್ಮ ವಿಳಾಸ',
        'set_placeholder_password': 'ಹೊಸ ಪಾಸ್‌ವರ್ಡ್ ನಮೂದಿಸಿ',
        
        // Categories
        'Food & Dining': 'ಆಹಾರ ಮತ್ತು ಊಟ',
        'Shopping': 'ಖರೀದಿ',
        'Transport': 'ಸಾರಿಗೆ',
        'Bills & Utilities': 'ಬಿಲ್ಲುಗಳು ಮತ್ತು ಉಪಯುಕ್ತತೆಗಳು',
        'Entertainment': 'ಮನರಂಜನೆ',
        'Other': 'ಇತರೆ'
    },
    'Hindi': {
        // Sidebar navigation
        'nav_dashboard': 'डैशबोर्ड',
        'nav_transactions': 'लेन-देन',
        'nav_calendar': 'कैलेंडर',
        'nav_reports': 'रिपोर्ट',
        'nav_settings': 'सेटिंग्स',
        'logout_btn': 'लॉग आउट',
        'search_placeholder': 'खोजें...',

        // Dashboard (index.html)
        'dash_title': 'डैशबोर्ड',
        'dash_btn_add_tx': 'लेन-देन जोड़ें',
        'card_total_balance': 'कुल शेष',
        'card_total_income': 'कुल आय',
        'card_total_spent': 'कुल खर्च',
        'card_spending_ratio': 'खर्च अनुपात',
        'chart_monthly_spending': 'मासिक खर्च',
        'chart_spending_label': 'खर्च',
        'recent_activity': 'हाल के लेनदेन',
        'no_transactions': 'कोई लेनदेन नहीं मिला',
        'loading_tx': 'लेनदेन लोड हो रहे हैं...',
        'warn_exceeded': 'चेतावनी: बजट सीमा पार हो गई!',
        'warn_exceeded_desc': 'आपका मासिक खर्च आपके बजट के $RATIO तक पहुँच गया है। अनावश्यक खर्चों को कम करने पर विचार करें।',

        // Transactions (transactions.html)
        'tx_title': 'लेन-देन जोड़ें',
        'tx_card_income': 'पैसे जोड़ें (आय)',
        'tx_source': 'स्रोत',
        'tx_amount': 'राशि',
        'tx_source_placeholder': 'जैसे: वेतन, फ्रीलांस कार्य',
        'tx_btn_add_income': 'आय जोड़ें',
        'tx_card_expense': 'खर्च जोड़ें',
        'tx_category': 'श्रेणी',
        'tx_select_category': 'श्रेणी चुनें',
        'tx_custom_category': 'नया श्रेणी नाम',
        'tx_custom_placeholder': 'श्रेणी का नाम दर्ज करें',
        'tx_recurring_bill': 'क्या यह आवर्ती बिल है?',
        'tx_btn_add_expense': 'खर्च जोड़ें',

        // Calendar (calendar.html)
        'cal_title': 'वित्तीय कैलेंडर',
        'cal_money_added': 'पैसे जोड़े गए (आय)',
        'cal_money_spent': 'पैसे खर्च किए गए (खर्च)',
        'cal_both': 'दोनों (आय और खर्च)',
        'cal_details': 'गतिविधि विवरण',
        'cal_click_inspect': 'लेनदेन का निरीक्षण करने के लिए किसी भी कैलेंडर दिन पर क्लिक करें',
        'cal_set_reminder': 'बिल / लंबित भुगतान अनुस्मारक सेट करें',
        'cal_rem_desc': 'विवरण (जैसे: इंटरनेट बिल)',
        'cal_rem_amount': 'राशि (वैकल्पिक)',
        'cal_save_reminder': 'अनुस्मारक सहेजें',
        'cal_scheduled': 'निर्धारित अनुस्मारक और बिल',
        'cal_loading_reminders': 'अनुस्मारक लोड हो रहे हैं...',
        'cal_no_reminders': 'कोई निर्धारित अनुस्मारक नहीं हैं।',

        // Reports (reports.html)
        'rep_title': 'वित्तीय रिपोर्ट',
        'rep_select_month': 'महीना चुनें',
        'rep_breakdown': 'खर्चों का वर्गीकरण',
        'rep_history': 'लेन-देने का इतिहास',
        'rep_no_spending': 'इस महीने के लिए कोई खर्च दर्ज नहीं किया गया है।',
        'rep_no_tx': 'इस महीने के लिए कोई लेनदेन दर्ज नहीं किया गया है',
        'rep_download_btn': 'परियोजना रिपोर्ट डाउनलोड करें',

        // Settings (settings.html)
        'set_title': 'सेटिंग्स',
        'set_profile': 'प्रोफ़ाइल विवरण',
        'set_name': 'नाम',
        'set_age': 'आयु',
        'set_gender': 'लिंग',
        'set_gender_select': 'चुनें...',
        'set_male': 'पुरुष',
        'set_female': 'महिला',
        'set_gender_other': 'अन्य',
        'set_phone': 'फ़ोन नंबर',
        'set_profession': 'पेशा',
        'set_profession_select': 'चुनें...',
        'set_student': 'छात्र',
        'set_professional': 'वर्किंग प्रोफेशनल',
        'set_business': 'व्यवसाय',
        'set_freelancer': 'फ्रीलांसर',
        'set_profession_other': 'अन्य',
        'set_address': 'पता',
        'set_save_changes': 'बदलाव सहेजें',
        'set_preferences': 'प्राथमिकताएं',
        'set_language': 'भाषा',
        'set_currency': 'मुद्रा और देश',
        'set_theme': 'ऐप थीम',
        'set_theme_light': 'लाइट मोड',
        'set_theme_dark': 'डार्क मोड',
        'set_theme_blue': 'ओशन ब्लू',
        'set_theme_green': 'फॉरेस्ट ग्रीन',
        'set_notifications': 'पुश नोटिफिकेशन',
        'set_notifications_desc': 'बिल और बजट सीमा के लिए अलर्ट प्राप्त करें',
        'set_security': 'सुरक्षा',
        'set_new_password': 'नया पासवर्ड',
        'set_update_password': 'पासवर्ड अपडेट करें',
        'set_save_all': 'सभी सेटिंग्स सहेजें',
        'set_placeholder_name': 'अपना नाम दर्ज करें',
        'set_placeholder_phone': 'फ़ोन नंबर',
        'set_placeholder_address': 'आपका पता',
        'set_placeholder_password': 'नया पासवर्ड दर्ज करें',
        
        // Categories
        'Food & Dining': 'भोजन और डाइनिंग',
        'Shopping': 'खरीदारी',
        'Transport': 'यात्रा',
        'Bills & Utilities': 'बिल और उपयोगिताएँ',
        'Entertainment': 'मनोरंजन',
        'Other': 'अन्य'
    }
};

function t(key) {
    const lang = localStorage.getItem('userLang') || 'English';
    if (translations[lang] && translations[lang][key]) {
        return translations[lang][key];
    }
    if (translations['English'] && translations['English'][key]) {
        return translations['English'][key];
    }
    return key;
}

function applyLanguage(lang) {
    if (!translations[lang]) return;
    
    // Save to local storage for persistence across pages
    localStorage.setItem('userLang', lang);

    // Apply translations to all elements with data-i18n attribute
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (translations[lang][key]) {
            // 1. If it's an input/textarea placeholder
            if ((el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') && el.hasAttribute('placeholder')) {
                el.setAttribute('placeholder', translations[lang][key]);
            } else {
                // 2. If it has a nested .i18n-text span (to protect icons)
                const span = el.querySelector('.i18n-text');
                if (span) {
                    span.textContent = translations[lang][key];
                } else {
                    // 3. Replace direct text node to preserve icons/formatting
                    let replaced = false;
                    for (let node of el.childNodes) {
                        if (node.nodeType === Node.TEXT_NODE && node.nodeValue.trim().length > 0) {
                            node.nodeValue = translations[lang][key];
                            replaced = true;
                            break;
                        }
                    }
                    // 4. Default fallback: set textContent directly
                    if (!replaced) {
                        el.textContent = translations[lang][key];
                    }
                }
            }
        }
    });
}

// Auto-apply on page load
document.addEventListener('DOMContentLoaded', () => {
    const savedLang = localStorage.getItem('userLang');
    if (savedLang) {
        applyLanguage(savedLang);
    }
});
