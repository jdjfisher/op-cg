
# Auto-generated at 2021-01-20 19:24:35.209878 by opcg


# Makefile generation is a wip




seq:
	$(FC) $(OPT) $(FMODS) -c \
		op_seq_save_soln.F90 op_seq_adt_calc.F90 op_seq_res_calc.F90 op_seq_bres_calc.F90 op_seq_update.F90 op_airfoil.F90 
	$(MPIF90) $(OPT) $(OPENMP) $(FLINK) -o exe_seq -lop2_for_seq \
		op_seq_save_soln.o op_seq_adt_calc.o op_seq_res_calc.o op_seq_bres_calc.o op_seq_update.o op_airfoil.o 

clean:
	rm -f exe_seq \
		op_seq_save_soln.F90 op_seq_adt_calc.F90 op_seq_res_calc.F90 op_seq_bres_calc.F90 op_seq_update.F90 op_airfoil.F90 \
		op_seq_save_soln.o op_seq_adt_calc.o op_seq_res_calc.o op_seq_bres_calc.o op_seq_update.o op_airfoil.o