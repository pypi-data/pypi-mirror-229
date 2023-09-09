import React from "react";
import { DetailPageEditForm } from "./DetailPageEditForm";
import _has from "lodash/has";
import _isEmpty from "lodash/isEmpty";
import { useFormConfig } from "@js/oarepo_ui/forms";

const VocabularyForm = () => {
  const { record, formConfig } = useFormConfig();
  const { vocabularyProps } = formConfig;
  const editMode = _has(formConfig, "updateUrl");
  const hasPropFields = !_isEmpty(vocabularyProps);
  const apiCallUrl = editMode ? formConfig.updateUrl : formConfig.createUrl;

  return (
    <DetailPageEditForm
      initialValues={record}
      hasPropFields={hasPropFields}
      apiCallUrl={apiCallUrl}
      editMode={editMode}
    />
  );
};

export default VocabularyForm;
