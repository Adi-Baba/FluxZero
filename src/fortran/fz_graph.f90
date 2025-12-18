module fz_graph
    use iso_c_binding
    implicit none

contains

    !----------------------------------------------------------------------
    ! Subroutine: fz_calc_flow_probs
    ! Description: Calculates flow probabilities (Softmax-ish) for children.
    !              Based on their 'Conductivity' (Win History).
    !----------------------------------------------------------------------
    subroutine fz_calc_flow_probs(n_children, conductivities, exploration, probs) &
            bind(c, name="fz_calc_flow_probs")
        integer(c_int), value :: n_children
        real(c_double), intent(in) :: conductivities(n_children)
        real(c_double), value :: exploration
        real(c_double), intent(out) :: probs(n_children)
        
        integer :: i
        real(c_double) :: sum_weight, weight
        
        sum_weight = 0.0d0
        
        do i = 1, n_children
            ! Weight = Conductivity + Exploration Pressure (UCB-like)
            ! O-ISH: Conductivity ~ 1/Resistance.
            ! We ensure weight > 0
            weight = conductivities(i)
            if (weight < 0.001d0) weight = 0.001d0
            
            ! Add Exploration (Noise/Temperature)
            weight = weight ** (1.0d0 / exploration) 
            
            probs(i) = weight
            sum_weight = sum_weight + weight
        end do
        
        ! Normalize
        if (sum_weight > 1e-9) then
            do i = 1, n_children
                probs(i) = probs(i) / sum_weight
            end do
        else
            ! Uniform if 0
            do i = 1, n_children
                probs(i) = 1.0d0 / real(n_children, c_double)
            end do
        end if
        
    end subroutine fz_calc_flow_probs

    !----------------------------------------------------------------------
    ! Subroutine: fz_update_conductivity
    ! Description: 'Erodes' the pipe. Updates conductivity based on outcome.
    !              Standard RL: Q(s,a) = Q(s,a) + alpha * (R - Q(s,a))
    !----------------------------------------------------------------------
    subroutine fz_update_conductivity(old_val, reward, learning_rate, new_val) &
            bind(c, name="fz_update_conductivity")
        real(c_double), value :: old_val, reward, learning_rate
        real(c_double), intent(out) :: new_val
        
        new_val = old_val + learning_rate * (reward - old_val)
        
    end subroutine fz_update_conductivity

end module fz_graph
