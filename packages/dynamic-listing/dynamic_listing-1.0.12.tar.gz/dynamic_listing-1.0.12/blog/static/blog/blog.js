var BulkDelete = function () {
  var form, deleteModal, bulkActionToggle, modalEl, actionToggle


  function initialize() {

    actionToggle.addEventListener('click', function (e) {
      e.preventDefault()
      BulkActions.addBulkActionsInputsToForm(
        form,
        this.getAttribute('data-input-type')
      )

    })
    bulkActionToggle.addEventListener('click', function (e) {
      e.preventDefault()
      BulkActions.addBulkActionsInputsToForm(
        form,
        this.getAttribute('data-input-type')
      )

    })

    modalEl.addEventListener('hidden.bs.modal', function () {
      BulkActions.resetBulkActionsInputs(form)
    })
  }

  return {
    init() {
      modalEl = document.getElementById('bulk-delete')
      deleteModal = new bootstrap.Modal(modalEl)
      bulkActionToggle = document.getElementById('delete-modal-bulk-action-toggle')
      actionToggle = document.getElementById('delete-modal-action-toggle')
      form = document.getElementById('delete-form')
      initialize()
    }
  }
}()


if (document.readyState !== 'loading' && document.body) {
  BulkDelete.init()
} else {
  document.addEventListener('DOMContentLoaded', BulkDelete.init)
}