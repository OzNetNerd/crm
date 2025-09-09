let childTaskCounter = 0;
let companies, contacts, opportunities;

// Initialize data from window globals set by the template
function initMultiTaskData(companiesData, contactsData, opportunitiesData) {
    companies = companiesData;
    contacts = contactsData;
    opportunities = opportunitiesData;
    
    // Add initial child tasks
    addChildTask();
    addChildTask();
}

function updateEntityOptions() {
    const entityType = document.getElementById('entity_type').value;
    const entitySelect = document.getElementById('entity_id');
    const container = document.getElementById('entity_select_container');
    
    if (!entityType) {
        container.style.display = 'none';
        return;
    }
    
    container.style.display = 'block';
    entitySelect.innerHTML = '<option value="">Select...</option>';
    
    let entities = [];
    if (entityType === 'company') entities = companies;
    else if (entityType === 'contact') entities = contacts;
    else if (entityType === 'opportunity') entities = opportunities;
    
    entities.forEach(entity => {
        const option = document.createElement('option');
        option.value = entity.id;
        option.textContent = entity.name;
        entitySelect.appendChild(option);
    });
}

function addChildTask() {
    childTaskCounter++;
    const container = document.getElementById('childTasksContainer');
    
    const childTaskDiv = document.createElement('div');
    childTaskDiv.className = 'border border-gray-200 rounded-lg p-4 bg-gray-50';
    childTaskDiv.id = `childTask-${childTaskCounter}`;
    
    childTaskDiv.innerHTML = `
        <div class="flex justify-between items-start mb-3">
            <h4 class="text-md font-medium text-gray-900">Child Task ${childTaskCounter}</h4>
            <button type="button" onclick="removeChildTask('childTask-${childTaskCounter}')"
                    class="text-red-600 hover:text-red-800 text-sm">Remove</button>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div class="md:col-span-2">
                <label class="block text-sm font-medium text-gray-700">Description</label>
                <textarea name="child_tasks[${childTaskCounter-1}][description]" rows="2" required
                          class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                          placeholder="Child task description..."></textarea>
            </div>
            
            <div>
                <label class="block text-sm font-medium text-gray-700">Priority</label>
                <select name="child_tasks[${childTaskCounter-1}][priority]" required
                        class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500">
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                    <option value="low">Low</option>
                </select>
            </div>
            
            <div>
                <label class="block text-sm font-medium text-gray-700">Due Date</label>
                <input type="date" name="child_tasks[${childTaskCounter-1}][due_date]"
                       class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500">
            </div>
            
            <div>
                <label class="block text-sm font-medium text-gray-700">Next Step Type</label>
                <select name="child_tasks[${childTaskCounter-1}][next_step_type]"
                        class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500">
                    <option value="">None</option>
                    <option value="call">Call</option>
                    <option value="email">Email</option>
                    <option value="meeting">Meeting</option>
                    <option value="demo">Demo</option>
                </select>
            </div>
        </div>
    `;
    
    container.appendChild(childTaskDiv);
}

function removeChildTask(taskId) {
    const taskDiv = document.getElementById(taskId);
    if (taskDiv) {
        taskDiv.remove();
    }
    
    // Ensure at least 2 child tasks remain
    const container = document.getElementById('childTasksContainer');
    if (container.children.length < 2) {
        addChildTask();
    }
}

// Form submission handler
function initMultiTaskForm() {
    document.getElementById('multiTaskForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const data = {};
        
        // Get parent task data
        data.description = formData.get('description');
        data.due_date = formData.get('due_date');
        data.priority = formData.get('priority');
        data.entity_type = formData.get('entity_type');
        data.entity_id = formData.get('entity_id');
        data.dependency_type = formData.get('dependency_type');
        
        // Get child tasks data
        data.child_tasks = [];
        const childTasksContainer = document.getElementById('childTasksContainer');
        const childDivs = childTasksContainer.querySelectorAll('[id^="childTask-"]');
        
        childDivs.forEach((childDiv, index) => {
            const description = childDiv.querySelector(`textarea[name*="description"]`).value.trim();
            if (description) {
                data.child_tasks.push({
                    description: description,
                    due_date: childDiv.querySelector(`input[name*="due_date"]`).value,
                    priority: childDiv.querySelector(`select[name*="priority"]`).value,
                    next_step_type: childDiv.querySelector(`select[name*="next_step_type"]`).value
                });
            }
        });
        
        if (data.child_tasks.length < 2) {
            alert('Multi Tasks must have at least 2 child tasks');
            return;
        }
        
        try {
            const response = await fetch('/tasks/multi/new', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            
            if (response.ok) {
                const result = await response.json();
                window.location.href = `/tasks/${result.task_id}`;
            } else {
                alert('Failed to create Multi Task');
            }
        } catch (error) {
            console.error('Error creating Multi Task:', error);
            alert('Failed to create Multi Task');
        }
    });
}