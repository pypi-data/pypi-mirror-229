Bulk Actions with Confirmation Messages User Manual
+++++++++++++++++++++++++++++++++++++++++++++++++++

Welcome to the User Manual for the Bulk Actions with Confirmation Messages feature. This feature empowers your web application with the ability to perform bulk actions, such as deleting multiple items, with built-in confirmation messages and customizable options. This manual will guide you through the integration and usage of this feature, ensuring enhanced user experience and security in your web application.


Using the Bulk Actions Feature
-------------------------------

To utilize the Bulk Actions feature effectively, follow these steps:

1. **Include Libraries:**

Ensure that your web application includes the required libraries:

- **SweetAlert Library:** This feature uses the SweetAlert library to display confirmation modals with custom messages and buttons.
- **Toastr Library:** Toastr is used for displaying notifications after successful actions or errors.


2. **Add Bulk Action Anchor Tags:**

To use the Bulk Actions feature, add an anchor tag with the `data-toggle="bulk-action"` attribute to your HTML. Customize the attributes for your specific use case. For instance, here's an example of a "Delete Selected" button:

.. code-block:: html

   <a href="/delete-articles/"
      data-request-method="POST"
      data-toggle="bulk-action"
      data-confirm-message="Are you sure you want to delete the selected articles?"
      data-input-type="selected">Delete Selected</a>

HTML Attributes Summary
~~~~~~~~~~~~~~~~~~~~~~~

Here's a summary of the HTML attributes used in the example:

.. list-table::
   :header-rows: 1

   * - Attribute
     - Is required
     - Options
     - Description
   * - data-toggle="bulk-action"
     - required
     - "bulk-action" (only: "bulk-action")
     - Specifies the use of the "bulk-action" feature.
   * - data-confirm-message
     - required
     - default: "Are you sure you would like to do this action!"
     - Customizable message that appears for confirmation message popup
   * - href
     - required
     -
     - URL for the action.
   * - data-request-method
     - optional
     - selected, queryset, none (default: "selected").
     - Determines the action target items:
       - **selected**: uses selected listing items ids as value
       - **queryset**: uses an object created of url querystring as value
       - **none**: the value is set to null
   * - data-input-type
     - required
     - GET, POST, PUT, DELETE, etc (default: GET).
     - HTTP method for the request.
   * - data-as-form
     - optional
     - default: "false"
     - Submits the request as form (requires a normal http response or redirect, not a json response)
   * - data-force-reload
     - optional
     - default: "true"
     - Reloads the page after action confirmed. When set to "false," it doesn't reload the page and uses the provided "data-callback" to handle the response.
   * - data-callback
     - required with `data-force-reload="false"`
     - default: ''
     - Executes the provided function in its value.
   * - data-confirm-icon
     - optional
     - warning, error, success, info, and question (default: 'warning')
     - Choose an icon for the confirmation modal.
   * - data-confirm-yes
     - optional
     - default: 'Yes, do it!'
     - Sets the popup confirmation dismiss button text.
   * - data-confirm-no
     - optional
     - default: 'No, cancel!'
     - Sets the popup confirmation dismiss button text.
   * - data-cancel-message
     - optional
     - default: "Your action has been cancelled!."
     - The message appears on dismissing the confirmation popup.
   * - data-cancel-icon
     - optional
     - warning, error, success, info, and question (default: 'error')
     - Choose an icon for the cancellation notification.
   * - data-cancel-action
     - optional
     - default: "Ok, got it!"
     - Sets the cancel notification button text.

**Define Callback Function**
Define the callback function, such as `handleDeletionCallback`, which will be called after the action is completed. If `data-force-reload` is set to `false`, the response data is accessible via the `this` keyword:

.. code-block:: html

       <a href="/delete-articles/"
          data-request-method="POST"
          data-toggle="bulk-action"
          data-confirm-message="Are you sure you want to delete the selected articles?"
          data-force-reload="false"
          data-callback="handleDeletionCallback"
          data-input-type="selected">Delete Selected</a>

       <script>
           function handleDeletionCallback() {
           console.log("Bulk deletion completed:", this);
           // Additional handling or notifications can be added here
           }
       </script>


Usage with Custom Forms
-----------------------

Sometimes you may want to build a bulk action with actual forms while still leveraging the functionality provided by the package. To achieve this, the package provides two functions for you:

1. `addBulkActionsInputsToForm` Function

   This function updates the form with the input `type` and `value` that you use in the request. Here's how to use it:

   .. code-block:: javascript

      var form = document.getElementById('delete-form');
      BulkActions.addBulkActionsInputsToForm(form, "selected");

   In this example, `addBulkActionsInputsToForm` is used to update the `delete-form` with the selected items' IDs as input values.

2. `resetBulkActionsInputs` Function

   This function resets the inputs in case of canceling an action. Here's how to use it:

   .. code-block:: javascript

      var form = document.getElementById('delete-form');
      BulkActions.resetBulkActionsInputs(form);

   In this example, `resetBulkActionsInputs` is used to reset the inputs in the `delete-form` after canceling an action.

These functions allow you to seamlessly integrate bulk actions with your custom forms, enhancing the usability and flexibility of the package.

.. note::
    before you use this section you might need to make sure the BulkActions method is initialized so you can use this function
    
    .. code-block:: javascript

        document.addEventListener('BulkActionsInitialized', function() {
      
          // your code here
        
        })
        


Handling Backend Views
----------------------

In your Django views, you might need to handle incoming data from HTTP requests, which can come in different formats. Here's an example of how you can handle incoming data using the code snippet provided:

.. code-block:: python

    if request.POST.keys():
        data = request.POST
    else:
        data = json.loads(request.body)

    if data['type'] == 'selected':
        value = data['value'].split(',')
    elif data['type'] == 'queryset':
        value = parse_qs(data['value'])
        for key in value:
            if len(value[key]) == 1:
                value[key] = value[key][0]
        value = dict(value)
    else:
        value = None

This code snippet demonstrates a common approach to handle incoming data in a Django view. It checks whether the data is provided via a POST request or in JSON format. Then, it processes the data based on its type, which can be 'selected' or 'queryset'.

- If the data type is 'selected', it splits the 'value' field by commas.
- If the data type is 'queryset', it parses the 'value' field into a dictionary, handling cases where values are lists.
- If the data type is something else, it sets 'value' to None.

You can adapt and extend this code to handle your specific use cases in Django views.


Troubleshooting
---------------

If you encounter issues or unexpected behavior while using the Bulk Actions with Confirmation Messages feature, consider the following troubleshooting tips:

1. **Check Button Attributes:**

   Double-check that you've correctly added the required attributes to your action buttons. Ensure that the `data-toggle` attribute is set to "bulk-action" for bulk actions to function properly.

2. **Library Dependencies:**

   Ensure you've included the SweetAlert and Toastr libraries in your project. Without these libraries, the confirmation modals and notifications won't work as intended.

3. **`csrfToken` Variable:**

   Remember to set the `csrfToken` variable before using the feature for authentication. This variable is crucial for CSRF protection when performing actions that modify data on the server.

4. **Error Handling:**

   If you encounter errors during bulk actions or confirmations, check your browser's console for detailed error messages. JavaScript errors or issues with library dependencies may be logged there.

By following these troubleshooting steps, you can identify and resolve common issues that may arise while using the Bulk Actions feature. If you continue to experience problems, consider reaching out to our support team for further assistance.

Conclusion
-----------

Congratulations! You've successfully integrated the "Bulk Actions with Confirmation Messages" feature into your web application. This powerful functionality enhances both the security and user experience when performing bulk actions within your application.

By following the usage instructions and customizing the provided HTML attributes, you can easily implement this feature to suit your specific use cases. Whether you need to delete multiple items, update records in bulk, or perform any other bulk action, this feature streamlines the process while ensuring user confirmation and notification.

Should you encounter any challenges or have questions regarding the integration or customization of this feature, please don't hesitate to reach out to our dedicated support team. We're here to assist you in making the most out of this valuable addition to your web application.

Thank you for choosing to enhance your web application with Bulk Actions and Confirmation Messages. We appreciate your trust in our solution, and we look forward to providing you with continued support and innovation in the future.

Happy coding!

.. raw:: pdf

   PageBreak