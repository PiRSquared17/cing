package cing.client;

import java.util.ArrayList;

import com.google.gwt.user.client.Event;
import com.google.gwt.user.client.Timer;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.ChangeListener;
import com.google.gwt.user.client.ui.CheckBox;
import com.google.gwt.user.client.ui.ClickListener;
import com.google.gwt.user.client.ui.DecoratorPanel;
import com.google.gwt.user.client.ui.FileUpload;
import com.google.gwt.user.client.ui.FlexTable;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.Image;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.ListBox;
import com.google.gwt.user.client.ui.Widget;
import com.gwtsolutions.components.client.ui.Message;

public class FileView extends iCingView {

    final Button startButton = new Button();
    final Button nextButton = new Button();
    final FlexTable flexTable = new FlexTable();
    final Button addButton = new Button();
    final HTML NRG_CING_HTML = new HTML();

    private final Message statusMessage = new Message("invisible empty msg", Message.SHAKE, 0.5);

    int i = 0;
    final int checkBoxIdx = i++;
    final int fileIdx = i++;
    final int programIdx = i++;
    final int typeIdx = i++;
    final int subTypeIdx = i++;
    final int otherIdx = i++;
    final int removeIdx = i++;
    final int submitIdx = i++;
    final int egIdx = i++;

    public FileView() {
        super();
        setState(iCing.FILE_STATE);
    }

    public void setIcing(iCing icing) {
        super.setIcing(icing);
        final iCing icingShadow = icing;

        Label label = new Label(c.Upload());
        label.setStylePrimaryName("h1");

        verticalPanel.add(label);
        verticalPanel.add(statusMessage);
        // Since there is no status initially, hide the status message
        statusMessage.setVisible(false);

        // Or visit NRG-CING for CING validation reports of an existing PDB NMR entry.
        String htmlText = "<P>"+c.Or_visit_NRG_CIN()+"</P>";
        htmlText = htmlText.replace("NRG-CING", "<A HREF=\"" + Settings.NRG_CING_URL + "\">NRG-CING</A>");
        NRG_CING_HTML.setHTML(htmlText);
        verticalPanel.add(NRG_CING_HTML);

        DecoratorPanel decPanel = new DecoratorPanel();
        final HorizontalPanel horizontalPanel = new HorizontalPanel();
        verticalPanel.add(decPanel);
        decPanel.add(horizontalPanel);
        horizontalPanel.setSpacing(11);

        final Image image = new Image();
        horizontalPanel.add(image);
        image.setUrl("images/paperclip.png");
        image.setSize("24", "24");

        horizontalPanel.add(flexTable);
        showStartButton();
        startButton.addClickListener(new ClickListener() {
            public void onClick(final Widget sender) {
                showUpload();
                addUploadRow();
            }
        });
        addButton.addClickListener(new ClickListener() {
            public void onClick(final Widget sender) {
                addUploadRow();
            }
        });
        showUpload();
        addUploadRow();

        final HorizontalPanel horizontalPanelBackNext = new HorizontalPanel();
        horizontalPanelBackNext.setSpacing(iCing.margin);
        verticalPanel.add(horizontalPanelBackNext);
        final Button backButton = new Button();
        horizontalPanelBackNext.add(backButton);
        backButton.addClickListener(new ClickListener() {
            public void onClick(final Widget sender) {
                icingShadow.onHistoryChanged(iCing.WELCOME_STATE);
            }
        });
        backButton.setText(c.Back());
        horizontalPanelBackNext.add(backButton);
        horizontalPanelBackNext.add(nextButton);

        nextButton.addClickListener(new ClickListener() {
            public void onClick(final Widget sender) {
                icingShadow.onHistoryChanged(iCing.CRITERIA_STATE);
            }
        });
//        nextButton.setEnabled(false);
        nextButton.setText(c.Next());
        nextButton.setTitle(c.Set_the_criteria());
    }

    public boolean showStartButton() {
        flexTable.setWidget(0, 0, startButton);
        startButton.setTitle(c.Select_file_s_());
        startButton.setText(c.Upload_file());
        startButton.setVisible(true);
        return false;
    }

    public boolean showUpload() {
        startButton.setVisible(false);
        final Label programLabel = new Label(c.Program());
        flexTable.setWidget(0, programIdx, programLabel);

        final Label typeLabel = new Label(c.Type());
        flexTable.setWidget(0, typeIdx, typeLabel);

        final Label subtypeLabel = new Label(c.Subtype());
        flexTable.setWidget(0, subTypeIdx, subtypeLabel);

        final Label otherLabel = new Label(c.Other());
        flexTable.setWidget(0, otherIdx, otherLabel);

        flexTable.setWidget(1, 1, addButton);
        addButton.setTitle(c.Add_another_upl());
        addButton.setText(c.Upload_another_f());
        addButton.setVisible(true);
        return false;
    }

    /**
     * flexTable ->cingQuerySave.formLayoutPanel
     *
     * @return true on error.
     */
    public boolean addUploadRow() {
        int currentRowIdx = flexTable.getRowCount() - 1;
//        if (currentRowIdx > 1) {
//            GenClient.showCodeBug("Not allowing more than one file now; one was already present.");
//            return true;
//        }
        flexTable.insertRow(currentRowIdx); // push the Add button down.
        /** Number the files in the table from 1 to n */
        @SuppressWarnings("unused")
        int currentFileNumber = flexTable.getRowCount() - 2;
//        GenClient.showDebug("Added file number [1,n]: " + currentFileNumber);

        final CheckBox checkBoxUseFile = new CheckBox();
        flexTable.setWidget(currentRowIdx, checkBoxIdx, checkBoxUseFile);
        checkBoxUseFile.setChecked(true);
        checkBoxUseFile.setText("");

        final Label labelFileUploadDone = new Label(c.This_message_sho());
        labelFileUploadDone.setVisible(false);

        Button submitButton = new Button(c.Upload());
        submitButton.setVisible(false);

        final FileUpload fileUpload = new FileUpload();
        fileUpload.setName(Settings.FORM_PARM_UPLOAD_FILE_BASE);
        // The GWT calls this formPanel handler after the formPanel is submitted.
        FormHandlerFile fileFormHandler = new FormHandlerFile(icing);
        fileFormHandler.setFileUpload(fileUpload);
        fileFormHandler.setLabelFileUploadDone(labelFileUploadDone);
        fileFormHandler.setStatusMessage(statusMessage);
        fileFormHandler.setSubmitButton(submitButton);
        fileFormHandler.setNextButton(nextButton);

        /** Invisible parameters to pass */

        final iCingQuery cingQuerySave = new iCingQuery(icing);
        cingQuerySave.action.setValue(Settings.FORM_ACTION_SAVE);
        cingQuerySave.setFormHandler(fileFormHandler); // Override the default one.
        cingQuerySave.formVerticalPanel.add(fileUpload); // will switch between these two.
        cingQuerySave.formVerticalPanel.add(labelFileUploadDone);

        flexTable.setWidget(currentRowIdx, fileIdx, cingQuerySave.formPanel);
        flexTable.setWidget(currentRowIdx, submitIdx, submitButton);

        final ListBox listBox_Program = new ListBox();
        final ListBox listBox_Type = new ListBox();
        final ListBox listBox_Subtype = new ListBox();
        final ListBox listBox_Other = new ListBox();
        final HTML egHtml = new HTML();

        fileFormHandler.setListBox_Program(listBox_Program);
        fileFormHandler.setListBox_Type(listBox_Type);
        fileFormHandler.setListBox_Subtype(listBox_Subtype);
        fileFormHandler.setListBox_Other(listBox_Other);
        fileFormHandler.setEgHtml(egHtml);

        /** Setup the 4 boxes */
        flexTable.setWidget(currentRowIdx, programIdx, listBox_Program);
        listBox_Program.setVisibleItemCount(1);
        ArrayList<String> programList = Classification.getProgramList();
        if (programList == null) { // impossible but modeled for consistency with below boxes.
            listBox_Program.addItem(iCing.STRING_NA);
        } else {
            for (String item : programList) {
                listBox_Program.addItem(item);
            }
        }
        listBox_Program.setItemSelected(0, true);
        if (listBox_Program.getItemCount() == 1) {
            listBox_Program.setEnabled(false);
        }
        listBox_Program.setFocus(true);

        flexTable.setWidget(currentRowIdx, typeIdx, listBox_Type);
        listBox_Type.setVisibleItemCount(1);
        String program = listBox_Program.getValue(listBox_Program.getSelectedIndex());
        ArrayList<String> typeList = Classification.getTypeList(program);
        if (typeList == null) { // impossible but modeled for consistency with below boxes.
            listBox_Type.addItem(iCing.STRING_NA);
        } else {
            for (String item : typeList) {
                listBox_Type.addItem(item);
            }
        }
        listBox_Type.setItemSelected(0, true);
        if (listBox_Type.getItemCount() == 1) {
            listBox_Type.setEnabled(false);
        }

        flexTable.setWidget(currentRowIdx, subTypeIdx, listBox_Subtype);
        listBox_Subtype.setVisibleItemCount(1);
        String type = listBox_Type.getValue(listBox_Type.getSelectedIndex());
        ArrayList<String> subTypeList = Classification.getSubTypeList(program, type);
        if (subTypeList == null || subTypeList.size() == 0) {
            listBox_Subtype.addItem(iCing.STRING_NA);
        } else {
            for (String item : subTypeList) {
                if (item == null) {
                    item = iCing.STRING_NA;
                }
                listBox_Subtype.addItem(item);
            }

        }
        listBox_Subtype.setItemSelected(0, true);
        if (listBox_Subtype.getItemCount() == 1) {
            listBox_Subtype.setEnabled(false);
        }

        flexTable.setWidget(currentRowIdx, otherIdx, listBox_Other);
        listBox_Other.setVisibleItemCount(1);
        String subType = listBox_Subtype.getValue(listBox_Subtype.getSelectedIndex());
        ArrayList<String> otherList = Classification.getOtherList(program, type, subType);
        if (otherList == null || otherList.size() == 0) {
            listBox_Other.addItem(iCing.STRING_NA);
        } else {
            for (String item : otherList) {
                if (item == null) {
                    item = iCing.STRING_NA;
                }
                listBox_Other.addItem(item);
            }
        }
        listBox_Other.setItemSelected(0, true);
        if (listBox_Other.getItemCount() == 1) {
            listBox_Other.setEnabled(false);
        }

        // setup timer to refresh list automatically
        Timer timer = new Timer() {
            public void run() {
                if (fileUpload.getFilename().length() == 0) {
                    return;
                }
                this.cancel();
                cingQuerySave.formPanel.submit();
            }
        };
        timer.scheduleRepeating(iCing.REFRESH_INTERVAL);

        checkBoxUseFile.addClickListener(new ClickListener() {
            public void onClick(final Widget sender) {
                int[] indices = Utils.getIndicesFromTable(flexTable, sender);
                if (indices == null) {
                    GenClient.showCodeBug("Failed to get getIndicesFromTable");
                    return;
                }
                flexTable.removeRow(indices[0]);
                if (flexTable.getRowCount() < 3) { // Start over.
                    Utils.removeAllRows(flexTable);
                    showStartButton();
                }
            }
        });

        listBox_Program.addChangeListener(new ChangeListener() {
            public void onChange(Widget sender) {
                updateListBox();
            }

            private void updateListBox() {
                // TODO: do same easy get for others...
                String program = Utils.getListBoxItemText(listBox_Program);
                ArrayList<String> typeList = Classification.getTypeList(program);
                listBox_Type.clear();
                for (String item : typeList) {
                    listBox_Type.addItem(item);
                }
                listBox_Type.setItemSelected(0, true);
                listBox_Type.setEnabled(typeList.size() > 1);
                listBox_Type.onBrowserEvent(Event.getCurrentEvent());
            }
        });

        listBox_Type.addChangeListener(new ChangeListener() {
            public void onChange(Widget sender) {
                updateListBox();
            }

            private void updateListBox() {
                int idx = listBox_Program.getSelectedIndex();
                if (idx < 0) {
                    GenClient.showError("Failed to get program");
                    return;
                }
                String program = listBox_Program.getValue(idx);
                idx = listBox_Type.getSelectedIndex();
                if (idx < 0) {
                    GenClient.showError("Failed to get type");
                    return;
                }
                String type = listBox_Type.getValue(idx);
                ArrayList<String> subTypeList = Classification.getSubTypeList(program, type);
                listBox_Subtype.clear();
                for (String item : subTypeList) {
                    listBox_Subtype.addItem(item);
                }
                listBox_Subtype.setItemSelected(0, true);
                listBox_Subtype.setEnabled(subTypeList.size() > 1);
                listBox_Subtype.onBrowserEvent(Event.getCurrentEvent());
            }
        });

        listBox_Subtype.addChangeListener(new ChangeListener() {
            public void onChange(Widget sender) {
                updateListBox();
            }

            private void updateListBox() {
                int idx = listBox_Program.getSelectedIndex();
                if (idx < 0) {
                    GenClient.showError("Failed to get program");
                    return;
                }
                String program = listBox_Program.getValue(idx);
                idx = listBox_Type.getSelectedIndex();
                if (idx < 0) {
                    GenClient.showError("Failed to get type");
                    return;
                }
                String type = listBox_Type.getValue(idx);
                idx = listBox_Subtype.getSelectedIndex();
                if (idx < 0) {
                    GenClient.showError("Failed to get subType");
                    return;
                }
                String subType = listBox_Subtype.getValue(idx);
                ArrayList<String> otherList = Classification.getOtherList(program, type, subType);
                listBox_Other.clear();
                for (String item : otherList) {
                    listBox_Other.addItem(item);
                }
                listBox_Other.setItemSelected(0, true);
                listBox_Other.setEnabled(otherList.size() > 1);
                listBox_Other.onBrowserEvent(Event.getCurrentEvent()); // No need to propagate
            }
        });

        listBox_Other.addChangeListener(new ChangeListener() {
            public void onChange(Widget sender) {
                updateListBox();
            }

            private void updateListBox() {
                setExample(listBox_Program, listBox_Type, listBox_Subtype, listBox_Other, egHtml);
            }
        });

        setExample(listBox_Program, listBox_Type, listBox_Subtype, listBox_Other, egHtml);
        flexTable.setWidget(currentRowIdx, egIdx, egHtml);

        submitButton.addClickListener(new ClickListener() {
            public void onClick(Widget sender) {
                cingQuerySave.formPanel.submit();
            }
        });

        return false;
    }

    void setExample(ListBox listBox_Program, ListBox listBox_Type, ListBox listBox_Subtype,
            ListBox listBox_Other, HTML egHtml) {
        /** Keep block together */
        String program = Utils.getListBoxItemText(listBox_Program);
        String type = Utils.getListBoxItemText(listBox_Type);
        String subType = Utils.getListBoxItemText(listBox_Subtype);
        String other = Utils.getListBoxItemText(listBox_Other);

        String egFilename = Classification.getExample(program, type, subType, other);

        String exampleUrl = "example/" + egFilename;
        exampleUrl = c.E_g_() + " <A HREF=\"" + exampleUrl + "\">"   + egFilename + "</a>";
        egHtml.setHTML(exampleUrl);
    }

    public void setEnableAllWidgetAtByRow(int row, boolean b) {
        int colCount = flexTable.getCellCount(row);
        for (int i = 0; i < colCount; i++) {
            Widget w = flexTable.getWidget(row, i);
            Utils.setEnabled(w, b);
        }
    }
}
