var BulkDelete = function () {
  var form, deleteModal, toggle, modalEl


  function initialize() {
    toggle.addEventListener('click', function (e) {
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
      toggle = document.getElementById('delete-modal-toggle')
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