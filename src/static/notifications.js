let ws = new WebSocket('ws://localhost:8000/api/notification/stream');
const notificationsList = document.getElementById('notificationsList');
const clearAllButton = document.getElementById('clearAll');

ws.onmessage = function(event) {
    const notifications = JSON.parse(event.data);
    notifications.forEach(notification => {
        addNotificationToUI(notification);
    });
};

ws.onclose = function() {
    console.log('Соединение с сервером прервано');
    setTimeout(connectWebSocket, 5000);
};

function addNotificationToUI(notification) {
    const notificationElement = createNotificationElement(notification);
    notificationsList.insertBefore(notificationElement, notificationsList.firstChild);
}

function createNotificationElement(notification) {
    const element = document.createElement('div');
    element.className = `notification ${notification.category || ''}`;
    element.dataset.id = notification.id;

    element.innerHTML = `
        <div class="notification-header">
            <h3>${notification.title}</h3>
            <span class="close-btn">×</span>
        </div>
        <div class="notification-content">
            <p>${notification.text}</p>
            <div class="notification-meta">
                <span class="date">${new Date(notification.created_at).toLocaleString('ru-RU')}</span>
                <span class="status ${notification.read_at ? 'read' : 'unread'}">
                    ${notification.read_at ? 'Прочитано' : 'Не прочитано'}
                </span>
                ${notification.category ? `<span class="category">${notification.category}</span>` : ''}
                ${notification.confidence ? `<span class="confidence">Вероятность: ${notification.confidence.toFixed(2)}</span>` : ''}
                ${notification.processing_status ? `<span class="process_status">${notification.processing_status}</span>` : ''}
            </div>
            <div class="notification-actions">
                <button class="btn refresh-btn" title="Обновить">
                    Обновить
                </button>
                ${!notification.read_at ? `
                    <button class="btn primary read-btn">
                        Прочитать
                    </button>
                ` : ''}
            </div>
        </div>
    `;

    element.querySelector('.close-btn').addEventListener('click', () => {
        element.remove();
    });

    const refreshBtn = element.querySelector('.refresh-btn');
    refreshBtn.addEventListener('click', async () => {
        try {
            refreshBtn.disabled = true;
            refreshBtn.classList.add('loading');

            const response = await fetch(`/api/notification/${notification.id}`);
            const updatedNotification = await response.json();

            if (response.ok) {
                updateNotificationElement(element, updatedNotification);
            }
        } catch (error) {
            console.error('Ошибка при обновлении уведомления:', error);
        } finally {
            refreshBtn.disabled = false;
            refreshBtn.classList.remove('loading');
        }
    });

    const readBtn = element.querySelector('.read-btn');
    if (readBtn) {
        readBtn.addEventListener('click', async () => {
            try {
                readBtn.disabled = true;
                readBtn.classList.add('loading');

                const response = await fetch(`/api/notification/${notification.id}/read`, {
                    method: 'PATCH'
                });
                const updatedNotification = await response.json();

                if (response.ok) {
                    updateNotificationElement(element, updatedNotification);
                }
            } catch (error) {
                console.error('Ошибка при отметке уведомления как прочитанного:', error);
            } finally {
                readBtn.disabled = false;
                readBtn.classList.remove('loading');
            }
        });
    }

    clearAllButton.addEventListener('click', () => {
        element.remove();
    });

    return element;
}

function updateNotificationElement(element, updatedNotification) {
    const titleElement = element.querySelector('h3');
    const textElement = element.querySelector('.notification-content p');
    const dateElement = element.querySelector('.date');
    const statusElement = element.querySelector('.status');
    const categoryElement = element.querySelector('.category');
    const confidenceElement = element.querySelector('.confidence');
    const processingStatusElement = element.querySelector('.notification-meta .process_status');
    const actionsDiv = element.querySelector('.notification-actions');

    titleElement.textContent = updatedNotification.title;
    textElement.textContent = updatedNotification.text;
    dateElement.textContent = new Date(updatedNotification.created_at).toLocaleString('ru-RU');

    if (updatedNotification.category) {
        if (!categoryElement) {
            const metaDiv = element.querySelector('.notification-meta');
            const categorySpan = document.createElement('span');
            categorySpan.className = 'category';
            categorySpan.textContent = updatedNotification.category;
            metaDiv.appendChild(categorySpan);
        } else {
            categoryElement.textContent = updatedNotification.category;
        }
    } else if (categoryElement) {
        categoryElement.remove();
    }

    if (updatedNotification.confidence) {
        if (!confidenceElement) {
            const metaDiv = element.querySelector('.notification-meta');
            const confidenceSpan = document.createElement('span');
            confidenceSpan.className = 'confidence';
            confidenceSpan.textContent = ` Вероятность: ${updatedNotification.confidence.toFixed(2)}`;
            metaDiv.appendChild(confidenceSpan);
        } else {
            confidenceElement.textContent = ` Вероятность: ${updatedNotification.confidence.toFixed(2)}`;
        }
    } else if (confidenceElement) {
        confidenceElement.remove();
    }

    if (updatedNotification.processing_status) {
        if (!processingStatusElement) {
            const metaDiv = element.querySelector('.notification-meta');
            const statusSpan = document.createElement('span');
            statusSpan.className = 'process_status';
            statusSpan.textContent = updatedNotification.processing_status;
            metaDiv.appendChild(statusSpan);
        } else {
            processingStatusElement.textContent = updatedNotification.processing_status;
        }
    } else if (processingStatusElement) {
        processingStatusElement.remove();
    }

    statusElement.textContent = updatedNotification.read_at ? 'Прочитано' : 'Не прочитано';
    statusElement.className = `status ${updatedNotification.read_at ? 'read' : 'unread'}`;

    actionsDiv.innerHTML = '';
    const refreshBtn = document.createElement('button');
    refreshBtn.className = 'btn refresh-btn';
    refreshBtn.title = 'Обновить';
    refreshBtn.innerHTML = 'Обновить';
    actionsDiv.appendChild(refreshBtn);

    if (!updatedNotification.read_at) {
        const readBtn = document.createElement('button');
        readBtn.className = 'btn primary read-btn';
        readBtn.textContent = 'Прочитать';
        actionsDiv.appendChild(readBtn);

        readBtn.addEventListener('click', async () => {
            try {
                const response = await fetch(`/api/notification/${updatedNotification.id}/read`, {
                    method: 'PATCH'
                });
                const finalNotification = await response.json();

                if (response.ok) {
                    updateNotificationElement(element, finalNotification);
                }
            } catch (error) {
                console.error('Ошибка при отметке уведомления как прочитанного:', error);
            }
        });
    } else {
        const readBtn = actionsDiv.querySelector('.read-btn');
        if (readBtn) {
            readBtn.classList.add('disabled');
            readBtn.disabled = true;
        }
    }
}

function connectWebSocket() {
    ws = new WebSocket('ws://localhost:8000/api/notification/stream');
    ws.onmessage = function(event) {
        const notifications = JSON.parse(event.data);
        notifications.forEach(notification => {
            addNotificationToUI(notification);
        });
    };
    ws.onclose = function() {
        console.log('Соединение с сервером прервано');
        setTimeout(connectWebSocket, 5000);
    };
}

clearAllButton.addEventListener('click', () => {
    notificationsList.innerHTML = '';
});
