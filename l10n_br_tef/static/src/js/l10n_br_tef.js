/******************************************************************************
 *    L10N_BR_TEF
 *    Copyright (C) 2018 KMEE INFORMATICA LTDA (http://www.kmee.com.br)
 *    @author Atilla Graciano da Silva <atilla.silva@kmee.com.br>
 *    @author Bianca da Rocha Bartolomei <bianca.bartolomei@kmee.com.br>
 *    @author Hugo Uchôas Borges <hugo.borges@kmee.com.br>
 *
 *    This program is free software: you can redistribute it and/or modify
 *    it under the terms of the GNU Affero General Public License as
 *    published by the Free Software Foundation, either version 3 of the
 *    License, or (at your option) any later version.
 *    This program is distributed in the hope that it will be useful,
 *    but WITHOUT ANY WARRANTY; without even the implied warranty of
 *    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *    GNU Affero General Public License for more details.
 *    You should have received a copy of the GNU Affero General Public License
 *    along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *
 ******************************************************************************/

openerp.l10n_br_tef = function(instance){
    module = instance.point_of_sale;

    var in_sequential = 2;
    var in_sequential_execute = 0;
    var io_connection = connect();
    var io_tags;
    var ls_transaction_global_value = '';
    var transaction_queue = new Array();
    var payment_type;

    function connect()
    {
        // Returns the established connection.
        return (new WebSocket('ws://localhost:60906'));
    }

    // Opens the connection and sends the first service
    io_connection.onopen = function()
    {
        // Reports that you are connected.
        trace('Connection successful');

        // Instantiate and initialize the tags for integration.
        io_tags = new tags();
        io_tags.initialize_tags();
    };

    /**
    Function for handling communication errors.
    */
    io_connection.onerror = function(error)
    {
        trace(error.data);
        //io_connection.close();
    };

    /**
    Function for receiving messages.
    */
    io_connection.onmessage = function(e){

        // Shows the message.
        trace("Received >>> " + e.data);

        // Initializes Tags.
        io_tags.initialize_tags();

        // Show the received Tags.
        disassembling_service(e.data);

        // If 'retorno' isn't OK
        if( io_tags.retorno !== "0" ) {
            in_sequential = io_tags.sequencial;
        }

        // Saves the current sequence of the collection.
        in_sequential_execute = io_tags.automacao_coleta_sequencial;

        setTimeout(function(){
            check_completed_consult();
            check_completed_execution();
            check_completed_send();
            check_inserted_card();
            check_filled_value();
            check_filled_value_send();
            check_inserted_password();
            check_approved_transaction();
            check_removed_card();
            finishes_operation();
        }, 1000);
    };

    function check_completed_consult(){

        if((io_tags.servico == "consultar") && (io_tags.retorno == "0")) {
            return true;
        }
        else if((io_tags.servico == '')&& (io_tags.retorno != "0")) {
            redo_operation(io_tags.sequencial);
            return false;
        }
    }

    function check_completed_execution(){
        if((io_tags.automacao_coleta_palavra_chave === "transacao_cartao_numero") &&
            (io_tags.automacao_coleta_retorno == "0")) {
            collect('');
        }else{
            //Handle Exceptions Here
        }
    }

    function check_completed_send(){
        if(io_tags.automacao_coleta_retorno == "0"){
            // Here the user must insert the card
        } else {
            //Handle Exceptions Here
        }
    }

    function check_inserted_card(){
        if((io_tags.automacao_coleta_palavra_chave === "transacao_valor") && (io_tags.automacao_coleta_mensagem === "Valor" )){
            // Transaction Value
            ls_transaction_global_value = $('.paymentline-input')[1]['value'].replace(',', '.');

            collect('');
        }
    }

    function check_filled_value(){
        if(io_tags.automacao_coleta_mensagem == "AGUARDE A SENHA"){
            ls_transaction_global_value = '';
            collect('');
        } else {
          // Handle Exceptions Here
        }
    }

    function check_filled_value_send(){
        // Aqui o usuário deverá preencher sua senha no PinPad
    }

    function check_inserted_password(){
        if(io_tags.automacao_coleta_mensagem === "Aguarde !!! Processando a transacao ..."){
            collect('');
        } else {
            // Handle Exceptions Here
        }
    }

    function check_approved_transaction(){
        if((io_tags.automacao_coleta_mensagem === "Transacao aprovada.") &&
            (io_tags.servico == "") && (io_tags.transacao == "")) {
            collect('');
        }else{
            // Handle Exceptions Here
        }
    }

    function check_removed_card(){
        if((io_tags.servico=="executar") && (io_tags.mensagem=="Transacao aprovada., RETIRE O CARTAO")){
            confirm(io_tags.sequencial);
            io_tags.mensagem = ""
        } else {
            // Handle Exceptions Here
        }
    }

    function finishes_operation(){
        if((io_tags.retorno=="1") && (io_tags.servico=="executar") && (io_tags.transacao=="Cartao Vender") ){
            finish();
        } else {
            // Handle Exceptions Here
        }
    }

    function trace(as_buffer) {
        console.log(as_buffer);
    }

    /**
    Necessary TAGs for integration.
    */
    function tags()
    {
        var aplicacao;
        var aplicacao_tela;
        var estado;
        var versao;
        var mensagem;
        var retorno;
        var sequencial;
        var servico;
        var transacao;
        var tipo_produto;
        var transacao_comprovante_1via;
        var automacao_coleta_palavra_chave;
        var transacao_comprovante_2via;
        var transacao_comprovante_resumido;
        var transacao_informacao;
        var transacao_opcao;
        var transacao_pagamento;
        var transacao_parcela;
        var transacao_produto;
        var transacao_rede;
        var transacao_tipo_cartao;
        var transacao_administracao_usuario;
        var transacao_administracao_senha;
        var transacao_valor;
        var automacao_coleta_sequencial;
        var automacao_coleta_retorno;
        var automacao_coleta_mensagem;
        var automacao_coleta_informacao;
        var automacao_coleta_opcao;

        this.fill_tags = function(as_tag, as_value)
        {

            if('automacao_coleta_opcao' === as_tag)
                this.automacao_coleta_opcao = as_value;

            else if ('automacao_coleta_informacao' === as_tag )
                this.automacao_coleta_informacao = as_value;

            else if ('automacao_coleta_mensagem' === as_tag)
                this.automacao_coleta_mensagem = as_value;

            else if ('automacao_coleta_retorno' === as_tag )
                this.automacao_coleta_retorno = as_value;

            else if ('automacao_coleta_sequencial' === as_tag)
                this.automacao_coleta_sequencial = as_value;

            else if ('transacao_comprovante_1via' === as_tag)
                this.transacao_comprovante_1via = as_value;

            else if ('transacao_comprovante_2via' === as_tag)
                this.transacao_comprovante_2via = as_value;

            else if ('transacao_comprovante_resumido' === as_tag)
                this.transacao_comprovante_resumido = as_value;

            else if ('servico' === as_tag)
                this.servico = as_value;

            else if ('transacao' === as_tag)
                this.transacao = as_value;

            else if ('transacao_produto' === as_tag)
                this.transacao_produto = as_value;

            else if ('retorno' === as_tag)
                this.retorno = as_value;

            else if ('mensagem' === as_tag)
                this.mensagem = as_value;

            else if ('sequencial' === as_tag)
                this.sequencial = parseInt(as_value,0);

            else if ('automacao_coleta_palavra_chave' === as_tag)
                this.automacao_coleta_palavra_chave = as_value;
        };

        this.initialize_tags = function()
        {
            this.transacao_comprovante_1via = '';
            this.transacao_comprovante_2via = '';
            this.transacao = '';
            this.transacao_produto = '';
            this.servico = '';
            this.retorno = 0;
            this.sequencial = 0;
        };
    }

    function disassembling_service(to_service) {

        var ln_start = 0;
        var ln_end = to_service.toString().indexOf("\n\r\n\t\t\r\n\t\t\t\r\n\t\t\r\n\t");
        var ls_tag = "";
        var ls_value = "";

        try {
            // While reading the received packet isn't finished ...
            while (ln_start < ln_end) {

                // Recovers the TAG..
                ls_tag = to_service.toString().substring(ln_start, to_service.indexOf('="', ln_start));
                ln_start = ln_start + (ls_tag.toString().length) + 2;

                ls_value = to_service.toString().substring(
                    ln_start, (ln_start = to_service.toString().indexOf('\"\n', ln_start)));

                ln_start += 2;
                
                io_tags.fill_tags(ls_tag, ls_value);
            }
        }
        catch (err) {
            alert('Internal Error: ' + err.message);
        }
    }

    function collect(ao_event)
    {
        if(ao_event == '') {
            send('automacao_coleta_sequencial="'+in_sequential_execute+'"automacao_coleta_retorno="0"automacao_coleta_informacao="'+ ls_transaction_global_value+ '"');
        }
    }

    function confirm(sequential)
    {
        var ls_transaction_type = "Cartao Vender";
        var ls_execute_tags = 'servico="executar"retorno="0"sequencial="'+ sequential + '"';

        ls_transaction_type = 'transacao="' + ls_transaction_type+'"';
        ls_execute_tags = ls_execute_tags + ls_transaction_type;

        send(ls_execute_tags);
    }

    function execute()
    {

        var ls_execute_tags = 'servico="executar"retorno="1"sequencial="'+ sequential() +'"';

        // var ls_card_type = (payment_type === "CD01")? "Debito" : "Credito";
        var ls_card_type = "Credito";
        var ls_transaction_type = "Cartao Vender";
        var ls_product_type = "Credito-Banrisul";
        var ls_payment_transaction = "A vista";


         if (ls_transaction_global_value !== "") {
             ls_transaction_global_value = 'transacao_valor="'+ls_transaction_global_value+'"';
             ls_execute_tags = ls_execute_tags+ls_transaction_global_value;
         }


         if (ls_transaction_type != "") {
             ls_transaction_type = 'transacao="'+ls_transaction_type+'"';
             ls_execute_tags = ls_execute_tags+ls_transaction_type;
         }

         if (ls_card_type != "") {
             ls_card_type  = 'transacao_tipo_cartao="'+ls_card_type+'"';
             ls_execute_tags = ls_execute_tags+ls_card_type;

         }

         if ( ls_payment_transaction != "") {
             ls_payment_transaction = 'transacao_pagamento="'+ls_payment_transaction+'"';
             ls_execute_tags = ls_execute_tags+ls_payment_transaction;
         }

         if ( ls_product_type != "" ){
             ls_product_type = 'transacao_produto="'+ls_product_type+'"';
             ls_execute_tags = ls_execute_tags+ls_product_type;
         }

         send(ls_execute_tags);
    }

    function send(as_buffer)
    {
        // Send the package.
        io_connection.send(as_buffer);

        // Places the current transaction in the queue
        transaction_queue.push(as_buffer);
        trace("Send >>> " + as_buffer);
    }

    function finish()
    {
        send('servico="finalizar"sequencial="'+sequential()+'"retorno="1"');
    }

    function consult()
    {
        send('servico="consultar"retorno="0"sequencial="'+ sequential()+'"');
    }

    function sequential()
    {
        // Incrementa o sequencial..
        in_sequential = (in_sequential+1);

        // document.getElementById('io_txt_sequencial').value = in_sequential;
        return(in_sequential);
    }

    function redo_operation(retorno_sequencial){
        if(transaction_queue.length > 0){
            setTimeout(function(){
                transaction_queue[transaction_queue.length-1] = transaction_queue[transaction_queue.length-1].replace(/sequencial="\d+"/, "sequencial=\"" + retorno_sequencial + "\"");
                    send(transaction_queue[transaction_queue.length-1]);
            }, 1000);
        }
    }

    function start_operation()
    {
        if (('consultar' === io_tags.servico)&& (io_tags.transacao_produto != '' )){
            execute();
        }
    }

    module.ProductScreenWidget.include({
        init: function(parent,options){
            this._super(parent,options);
            consult();
        }
    });

    module.PaymentScreenWidget.include({
        rerender_paymentline: function(line) {
            this._super(line);
        },
        render_paymentline: function(line){
            el_node = this._super(line);
            var self = this;
             
            if (["CD01", "CC01"].indexOf(line.cashregister.journal.code) > -1 &&
                this.pos.config.iface_tef){
                payment_type = line.cashregister.journal.code;

                el_node.querySelector('.payment-terminal-transaction-start')
                    .addEventListener('click', function(){start_operation()});
            }
            return el_node;
        },
    });
};